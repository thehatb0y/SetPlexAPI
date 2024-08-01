# Norago.tv API Script

This script provides functions for interacting with the Norago.tv API. 

**Requirements:**

* `requests` library: You can install it using `pip install requests`

**Environment Variables:**

* `subdomain`: Your Norago.tv subdomain.
* `token`: Your Norago.tv API token.
* `login`: Your Norago.tv login.

**User Info Test Setup (Modify for real test):**

* `first_name`: Placeholder for user's first name.
* `last_name`: Placeholder for user's last name.
* `phone`: Placeholder for user's phone number.
* `email`: Placeholder for user's email address.
* `account_number`: Placeholder for user's account number.

**How to Use:**

1. Set the required environment variables.
2. Run the script: `python script.py` (replace `script.py` with your actual filename)

**Available Functions:**

* `create_user(subdomain, token, login, first_name, last_name, phone, email)`: Creates a new user.
* `search_subscriber(subdomain, token, login, email)`: Searches for a subscriber by email.
* `make_payment(subdomain, token, login, account_number, last_name, subscription_id)`: Makes a payment for a subscription.
* `get_sub_info(subdomain, token, login, last_name, account_number)`: Gets information about a subscriber.
* `remove_device(subdomain, token, login, last_name, account_number, device_number)`: Removes a device from a subscriber's account.
* `delete_subscriber(subdomain, token, login, last_name, account_number)`: Deletes a subscriber.
* `remove_all_devices(subdomain, token, login, last_name, account_number)`: Removes all devices from a subscriber's account.
* `get_activation_codes(subdomain, token, login, last_name, account_number)`: Gets a list of activation codes for a subscriber.
* `renew_activation_code(subdomain, token, login, last_name, account_number, activation_code_id)`: Renews a single activation code.
* `renew_all_activation_codes(subdomain, token, login, last_name, account_number)`: Renews all activation codes for a subscriber.
* `get_packages_info(subdomain, token, login)`: Gets information about the subscriber's packages.
* `get_network_info(subdomain, token, login)`: Gets information about the Norago.tv network.

**Main Menu (Interactive Mode):**

The script also provides an interactive menu for easy access to the functionalities. Run the script and follow the prompts.

**Disclaimer:**

This script is for educational purposes only. Please refer to the Norago.tv API documentation for official usage guidelines.
