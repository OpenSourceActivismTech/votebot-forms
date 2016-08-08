from __future__ import unicode_literals
from base_ovr_form import BaseOVRForm, OVRError
from form_utils import split_date, bool_to_int, log_form, get_party_from_list, options_dict


class VoteDotOrg(BaseOVRForm):

    def __init__(self, partner_id=None):
        VOTEORG_URL = 'https://register.vote.org/'
        if partner_id:
            VOTEORG_URL += '?partner=%s' % partner_id
        super(VoteDotOrg, self).__init__(VOTEORG_URL)
        self.add_required_fields(['political_party', 'email'])

    def parse_errors(self):
        messages = []
        for error in self.browser.find_all(class_='usa-alert-error'):
            messages.append(error.find(class_='usa-alert-body').text)
        return messages

    def get_started(self, user):
        form = self.browser.get_form(id='get_started_form')
        form['first_name'].value = user['first_name']
        form['last_name'].value = user['last_name']

        # date_of_birth -> parts
        (year, month, day) = split_date(user['date_of_birth'], padding=False)
        form['date_of_birth_month'].value = month
        form['date_of_birth_day'].value = day
        form['date_of_birth_year'].value = year

        # street address
        # can't figure out how to bypass autocomplete, so reassemble parts into string
        form['address_autocomplete'] = '%(address)s, %(city)s, %(state)s %(zip)s' % user

        # contact
        form['email'] = user.get('email')
        form['mobile_phone'] = user['phone']

        log_form(form)
        self.browser.submit_form(form)

        return form

    def full_registration(self, user):
        # if given choice to register online, choose pdf form
        if self.browser.get_form(id='state_ovr'):
            finish_form = self.browser.get_form(id='finish')
            log_form(finish_form)
            self.browser.submit_form(finish_form)

        full_form = self.browser.get_form(id='full_registration')
        if full_form:
            # BUG, user.get(field, '') results in silent 400 errors, wtf?
            # full_form['title'].value = user.get('title', '')
            # print 'set title', full_form['title'].value
            # full_form['suffix'].value = user.get('suffix', '')
            # print 'set suffix', full_form['suffix'].value

            full_form['state_id_number'].value = user['id_number']

            party_translated = get_party_from_list(user.get('political_party'), options_dict(full_form['political_party']).keys())
            full_form['political_party'].value = options_dict(full_form['political_party'])[party_translated]
            # why does the form require bool as string?
            full_form['us_citizen'].value = str(bool_to_int(user['us_citizen']))

            log_form(full_form)
            self.browser.submit_form(full_form)

        else:
            errors_string = ','.join(self.parse_errors())
            raise OVRError('unable to get_form full_registration: ' + errors_string, payload=self.browser.parsed)

    def get_download(self, user):
        self.browser.open('https://register.vote.org/downloads.json')
        download_response = self.browser.state.response.json()
        if download_response['status'] == 'ready':
            return True

    def submit(self, user):
        self.validate(user)
        self.get_started(user)

        # todo: handle some state specific logic:

        # vote.org has messaging for these:
            # New Hampshire: town and city clerks will accept this application only as a request for their own absentee voter mail-in registration form.
            # Wyoming: law does not permit mail registration

        # but interestingly does not cover:
            # North Dakota: does not have voter registration. (it's not required!)

        self.full_registration(user)

        # todo: get_download really needs to be async / queued.
        return {'status': 'queued'}
