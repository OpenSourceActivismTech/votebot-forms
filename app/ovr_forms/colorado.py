from base_ovr_form import BaseOVRForm
from form_utils import bool_to_string, split_date, options_dict


class Colorado(BaseOVRForm):
    def __init__(self):
        super(Colorado, self).__init__('https://www.sos.state.co.us/voter-classic/pages/pub/olvr/verifyNewVoter.xhtml')
        self.required_fields.extend(['is_military', 'vote_by_mail',
                'military_overseas', 'gender', 'legal_resident', 'consent_use_signature'])

    def submit(self, user):
        self.verify_identification(user)
        self.edit_voter_information(user)
        self.review(user)
        self.affirmation(user)

    def verify_identification(self, user):
        verify_identification_form = self.browser.get_form(id='verifyNewVoterForm')

        verify_identification_form['verifyNewVoterForm:voterSearchLastId'].value = user['last_name']
        verify_identification_form['verifyNewVoterForm:voterSearchFirstId'].value = user['first_name']

        (year, month, day) = split_date(user['date_of_birth'])
        verify_identification_form['verifyNewVoterForm:voterDOB'].value = '/'.join(month, day, year)

        verify_identification_form['verifyNewVoterForm:driverId'].value = user['id_number']

        self.browser.submit_form(verify_identification_form, submit=verify_identification_form['verifyNewVoterForm:voterSearchButtonId'])

    def edit_voter_information(self, user):
        edit_voter_form = self.browser.get_form(id='editVoterForm')

        # choices for party:
        # <select id="editVoterForm:partyAffiliationId_input" name="editVoterForm:partyAffiliationId_input">
        #     <option value=""></option>
        #     <option value="ACN">American Constitution</option>
        #     <option value="DEM" selected="selected">Democratic</option>
        #     <option value="GRN">Green</option>
        #     <option value="LBR">Libertarian</option>
        #     <option value="REP">Republican</option>
        #     <option value="UAF">Unaffiliated</option>
        #     <option value="UNI">Unity</option>
        # </select>
        edit_voter_form['editVoterForm:partyAffiliationId_input'].value = options_dict(edit_voter_form['editVoterForm:partyAffiliationId_input'])[user['party_affiliation']]

        if user['is_military'] or user['overseas']:
            edit_voter_form['editVoterForm:areUOCAVAId'].value = 'Y'
            edit_voter_form['editVoterForm:uocavaTypeId'].value = 'a' if user['is_military'] else 'c'
        else:
            edit_voter_form['editVoterForm:areUOCAVAId'].value = 'N'

        edit_voter_form['editVoterForm:uocavaBallotMethodId'].value = 'Mail' # or 'Fax' or 'Email'

        # todo: these seem optional or debatable
        # email, phone and gender are prefilled
        edit_voter_form['editVoterForm:emailId'].value = user['email']
        edit_voter_form['editVoterForm:receiveEmailCommunicationId'].value = user['receive_election_info_by_email']
        edit_voter_form['editVoterForm:phoneId'].value = user['phone']
        edit_voter_form['editVoterForm:genderSelectId'].value = '0' if user['gender'] == 'F' else '1'

        edit_voter_form['editVoterForm:resAddress'].value = user['home_address']
        edit_voter_form['editVoterForm:resCity'].value = user['home_city']

        # todo:
        county = None
        edit_voter_form['editVoterForm:resCounty_input'].value = options_dict(edit_voter_form['editVoterForm:resCounty_input'])[county]

        edit_voter_form['editVoterForm:resZip'].value = user['home_zip']

        self.browser.submit_form(edit_voter_form, submit=edit_voter_form['editVoterForm:j_idt113'])

    def review(self, user):
        review_form = self.browser.get_form(id='reviewVoterForm')
        # noop
        self.browser.submit_form(review_form, submit=review_form['reviewVoterForm:j_idt86'])

    def affirmation(self, user):
        affirmation_form = self.browser.get_form(id='affirmationVoterForm')

        # this field name jumps out at me...

        # I am aware that if I
        # register to vote in Colorado I am also considered a resident
        # of Colorado for motor vehicle registration and operation
        # purposes and for income tax purposes.
        if user['legal_resident']:
            affirmation_form['affirmationVoterForm:crimminalActId'].checked = 'checked'


        # I might want some help dicing this up into fields:
        
        # I affirm that I am a citizen of the United States; I have been a
        # resident of the state of Colorado for at least twenty-two
        # days immediately prior to an election in which I intend to
        # vote; and I am at least sixteen years old and understand
        # that I must be eighteen years old to be eligible to vote. I
        # further affirm that my present address as stated herein is
        # my sole legal place of residence, that I claim no other
        # place as my legal residence, and that I understand that I am
        # committing a felony if I knowingly give false information
        # regarding my place of present residence. I certify under
        # penalty of perjury that I meet the registration
        # qualifications; that the information I have provided on this
        # application is true to the best of my knowledge and belief;
        # and that I have not, nor will I, cast more than one ballot
        # in any election.
        if False:
            affirmation_form['affirmationVoterForm:affirmCtizId'].checked = 'checked'


        if user['consent_use_signature']:
            affirmation_form['affirmationVoterForm:fromStatueId'].checked = 'checked'

        self.browser.submit_form(affirmation_form, submit=affirmation_form['affirmationVoterForm:j_idt73'])





