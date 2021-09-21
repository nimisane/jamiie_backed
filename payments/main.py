from utilFunctions import *

# change these urls according to yours...
jamiie_account_url = 'https://api-sandbox.dwolla.com/accounts/6b9567e8-825a-4198-be03-e0ee875459ea'
jamiie_funding_src = "https://api-sandbox.dwolla.com/funding-sources/5d09b038-c2a3-4f29-a7ac-6b9559f75043"
customer_url = 'https://api-sandbox.dwolla.com/customers/a189d0f5-04eb-4e32-b910-3c9c07691ded'
customer_url2 = "https://api-sandbox.dwolla.com/customers/8fec57ed-03b0-4395-a7ac-89d51a079494"
document_url = 'https://api-sdandbox.dwolla.com/documents/b20b6cc1-fb1c-48aa-b699-ef3d0d892175'
funding_src = "https://api-sandbox.dwolla.com/funding-sources/7b933cb8-5ade-48f7-a1ce-f2666a12f810"

jamiie_account = {
    'routingNumber': '222222226',
    'accountNumber': '123456789',
    'bankAccountType': 'checking',
    'name': 'My Bank'
}

customer_details = request_body = {
    'firstName': 'Batisddhah',
    'lastName': 'Paritoddshah',
    'email': 'batishparitddoashh2@gmail.com',
    'type': 'personal',
    'address1': '99-99 33rd St',
    'city': 'Some City',
    'state': 'NY',
    'postalCode': '11101',
    'dateOfBirth': '1970-01-01',
    # For the first attempt, only the
    # last 4 digits of SSN required
    # If the entire SSN is provided,
    # it will still be accepted
    'ssn': '1224'
}

# https://docs.dwolla.com/#transfers
# details for request json
transfer_body = {
    '_links': {
        'source': {
            'href': jamiie_funding_src
        },
        'destination': {
            'href': funding_src
        }
    },
    'amount': {
        'currency': 'USD',
        'value': '1.00'
    },
    'metadata': {
        'paymentId': '12345678',
        'note': 'payment for completed work Dec. 1'
    },
    'clearing': {
        'destination': 'next-available'
    }
}

mass_payment_body = {
    '_links': {
        'source': {
            'href': jamiie_funding_src
        }
    },
    'achDetails': {
        'addenda': {
            'values': ['ABC123_AddendaValue']
        }
    },
    'clearing': {
        'source': 'standard'
    },
    'items': [
        {
            '_links': {
                'destination': {
                    'href': customer_url
                }
            },
            'amount': {
                'currency': 'USD',
                'value': '1.00'
            },
            'clearing': {
                'destination': 'next-available'
            },
            'metadata': {
                'payment1': 'payment1'
            },
            'correlationId': 'ad6ca82d-59f7-45f0-a8d2-94c2cd4e8841',
            'achDetails': {
                'addenda': {
                    'values': ['ABC123_AddendaValue']
                }
            }
        },
        {
            '_links': {
                'destination': {
                    'href': customer_url2
                }
            },
            'amount': {
                'currency': 'USD',
                'value': '5.00'
            },
            'clearing': {
                'destination': 'next-available'
            },
            'metadata': {
                'payment2': 'payment2'
            },
            'achDetails': {
                'addenda': {
                    'values': ['ABC123_AddendaValue']
                }
            }
        }
    ],
    'metadata': {
        'batch1': 'batch1'
    },
    'correlationId': '6d127333-69e9-4c2b-8cae-df850228e130'
}

## Setup owner account
# owner_acc_details()
# owner_funding_src(jamiie_account)
# get_owner_funding_src(jamiie_account_url)
# initiate_micro_deposits(jamiie_funding_src)
# verify_micro_deposits(jamiie_funding_src)


## Setting up customer
# create_customer(customer_details)
# customer_status(customer_url)
# get_customers(10)
# upload_customer_documents(jamiie_account_url)
get_iav_token(customer_url)
# retrieve_funding_src(funding_srdwc)
# initiate_transfer(transfer_body)

## Mass payments
# mass_payments(mass_payment_body)
