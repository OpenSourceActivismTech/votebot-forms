# VoteBot-Forms

## Motivation
Online voter registration should be easy. Unfortunately, each state has their own form design. This application provides a nice API that abstracts across them, and falls back to the National Mail Voter Registration Form PDF when online registration is not possible.

## Usage
POST to your desired form endpoint ('/pdf' or '/ovr') with json like
```
{ 
  callback_url: '/callback',
  user: {
    "first_name":"John",
    "middle_name":"Q",
    "last_name":"Public",
    "date_of_birth":"1950-12-25",
    "address":"314 Test St",
    "address_unit": "#1"
    "city":"Schenectady",
    "state":"NY",
    "zip":"12345",
    "phone":"123-456-7890",
    "email":"text@example.com"
    "state_id_number":"NONE",
    "ssn_last4": 0000,
    "political_party":"No Party",
    "us_citizen":true,
    "legal_resident": true,
    "disenfranchised":false,
    "has_previous_name": false,
    "has_previous_address": false
  }
}
```

receive a response like
```
{
    "status": "queued"
}
```

get a POST to your callback_url like
```
{
    "status": "success", // for print and mail
    "pdf_url": "https://hellovote.s3.amazonaws.com/forms/UUID/hellovote-registration-print-me.pdf"
}
```
or 
```
{
    "status": "success", // for state OVR
    "missing_fields": []
}
```

## Status
Currently works in:
- Alaska
- Arizona
- Colorado
- Georgia
- Hawaii
- Illinois
- Kentucky
- Massachusetts
- Vermont
- Virginia
- West Virginia

Has worked in:
- California (blocked by [#1](https://github.com/fightforthefuture/votebot-forms/issues/1))

Could work in:
- Pennsylvania (code written in [feature/pennsyvanlia-api](https://github.com/fightforthefuture/votebot-forms/tree/pennsylvania-api), deployment was delayed in 2016 due to testing timeline)

## PDF Form
The PDF form is generated from the [National Mail Voter Registration Form](http://www.eac.gov/voter_resources/register_to_vote.aspx), with a custom instructions and mailing page. These are combined with PDFTK and filled in with an FDF data stream before being uploaded to Amazon S3 for user download.

If the registration POST data has a flag `include_postage` set to true, we will generate an stamp a pre-paid USPS mailing label to from the user's home address to their local election official with EasyPost. This costs us real money, so don't enable the flag unless we've confirmed that the user does not have access to a printer and stamp at home.

If the registration POST data has a flag `mail_letter` set to true, we will print and mail the generated form to the user with Lob.com. This costs us real money, so don't enable the flag unless we've confirmed that the user does not have access to a printer and stamp at home.

The `include_postage` and `mail_letter` flags are not mutually exclusive, you must enable both to mail a letter with an included postage label.

## Development
- `docker-compose build`
- `docker-compose up`

## Adding new states
Votebot-forms can only work with states that have online voter registration systems (OVR) without access control (user login, captcha, etc). Because we are submitting on behalf of the user, we will not do any work to circumvent access controls. 

To create a new state integration:

- add a new file called STATE.py to `app/ovr_forms`
- create a class that inherits from `BaseOVRForm`
- add required fields, making sure to match the [field taxonomy](https://docs.google.com/a/fightforthefuture.org/spreadsheets/d/11MoK-p-yOpZGrQ0-Y-_Ffdm1T4niYtsSut4UC6U60FQ/edit). If you need to define a new field, you'll also need to add it to votebot-api, to make sure we are asking users with the correct phrasing.
- start the state submission process in a browser, and get as far as you can without a local ID
- finish the form with a volunteer's ID, after getting one from the FFTF volunteer coordinator
- add unit tests to `tests/ovr_forms/test_STATE.py`
- when the form is tested, add it to the OVR_FORMS dict in `app/ovr_forms/__init__.py`

## Testing
- fill `tests/secrets.yml` with valid identification information. ensure dates are iso-formatted strings
- eg `
    NY: 
      first_name: John
      middle_name: Q
      last_name: Public
      date_of_birth: "1950-12-25"
      address: 314 Test St
      city: Schenectady
      state: NY
      zip: 12345
      phone: 123-456-7890
      email: text@example.com
      state_id_number: NONE,
      ssn_last4: 0000,
      political_party: No Party
      us_citizen:true
      legal_resident:true
      disenfranchised:false
`
- ssh into the web container `docker-compose run web bash`
- run `nosetests tests/`

## Security
- Requires PyOpenSSL and ndg-httpsclient for improved SSL certificate validation. California's system won't validate without it...
- If an environment variable `VOTEBOT_API_KEY` is set, we will require all POSTs to registration endpoints /pdf and /ovr to include it in an HTTP Basic Auth header.

## Deployment
VBF is set up to deploy on kubernetes using a managed database service and container registry.

To deploy:
 - uncomment the `heroku` requirements in the dockerfiles and build the production images: `docker-compose build`
 - tag the images: `docker tag [SOURCE_IMAGE] [HOSTNAME]/[PROJECT-ID]/[IMAGE]:[TAG]`
 - push the tagged images to the container registry: `docker push [HOSTNAME]/[PROJECT-ID]/[IMAGE]`
 - update the `image` in `docker-compose.prod.yml` to point to the newly tagged images
 - update `ENV` vars in `docker-compose.prod.yml` with the IP of the database host and other production vars
 - create the Kubernetes deployment with `kompose up -f docker-compose.prod.yml`
