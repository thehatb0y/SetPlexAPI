import requests
import random
import json
import os

def create_user(subdomain, token, login, first_name, last_name, phone, email):
    url = f'https://{subdomain}.norago.tv/apex/v2/subscribers/create'
    
    # Gerar números aleatórios de 9 dígitos
    username = str(random.randint(100000000, 999999999))
    password = str(random.randint(100000000, 999999999))
    
    data = {
        "auth": {
            "token": token,
            "login": login
        },
        "userName": username,
        "password": password,
        "pinCode": "1234",
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": phone,
        "zipCode": "1840000",
        "address": "victoria 381",
        "city": "ovalle",
        "country": "CL",
        "state": "",
        "timeZone": "America/Santiago",
        "language": "English",
        "dateOfBirth": ""
    }
    
    response = requests.post(url, json=data)
    return response.json()

def search_subscriber(subdomain, token, login, email):
    url = f'https://{subdomain}.norago.tv/apex/v2/subscribers/search'
    
    data = {
        "auth": {
            "token": token,
            "login": login
        },
        "email": email
    }
    
    response = requests.post(url, json=data)
    return response.json()

def make_payment(subdomain, token, login, account_number, last_name, subscription_id):
    url = f'https://{subdomain}.norago.tv/apex/v2/payments/do'
    
    data = {
        "auth": {
            "token": token,
            "login": login,
            "accountNumber": account_number,
            "lastName": last_name
        },
        "deviceCount": 4,
        "subscriptionId": subscription_id,
        "approvalRequired": False,
        "paymentSystemType": "CASH"
    }
    
    response = requests.post(url, json=data)
    return response.json()

def get_sub_info(subdomain, token, login, last_name, account_number):
    url = f'https://{subdomain}.norago.tv/apex/v2/subscribers/get'
    
    data = {
        "auth": {
            "token": token,
            "login": login,
            "accountNumber": account_number,
            "lastName": last_name
        }
    }
    
    response = requests.post(url, json=data)
    return response.json()

def remove_device(subdomain, token, login, last_name, account_number, device_number):
    url = f'https://{subdomain}.norago.tv/apex/v2/subscribers/devices/{device_number}/unassign'
    
    data = {
        "auth": {
            "token": token,
            "login": login,
            "accountNumber": account_number,
            "lastName": last_name
        }
    }
    
    response = requests.post(url, json=data)
    return response.json()

def delete_subscriber(subdomain, token, login, last_name, account_number):
    url = f'https://{subdomain}.norago.tv/apex/v2/subscribers/delete'
    
    data = {
        "auth": {
            "token": token,
            "login": login,
            "accountNumber": account_number,
            "lastName": last_name
        }
    }
    
    response = requests.post(url, json=data)
    return response.json()

def remove_all_devices(subdomain, token, login, last_name, account_number):
    # Obter informações do assinante
    sub_info = get_sub_info(subdomain, token, login, last_name, account_number)
    
    # Verificar se a resposta foi bem-sucedida
    if sub_info.get('status', {}).get('code') != '0':
        print("Erro ao obter informações do assinante")
        return
    
    # Obter todos os serialNumbers dos dispositivos
    devices = sub_info.get('result', {}).get('devices', [])
    for device in devices:
        serial_number = device.get('serialNumber')
        if serial_number:
            # Remover o dispositivo
            result = remove_device(subdomain, token, login, last_name, account_number, serial_number)
            
            # Verificar se a remoção foi bem-sucedida
            if result.get('status', {}).get('code') == '0':
                print(f"Dispositivo {serial_number} removido com sucesso.")
            else:
                print(f"Erro ao remover o dispositivo {serial_number}.")

def get_activation_codes(subdomain, token, login, last_name, account_number):
    url = f'https://{subdomain}.norago.tv/apex/v2/activationcodes/get'
    
    data = {
        "auth": {
            "token": token,
            "login": login,
            "accountNumber": account_number,
            "lastName": last_name
        }
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    # Verificar se a resposta foi bem-sucedida
    if result.get('status', {}).get('code') != '0':
        print("Erro ao obter códigos de ativação")
        return None
    
    # Extrair a lista de activationCodeId
    activation_codes = result.get('result', [])
    activation_code_ids = [code.get('activationCodeId') for code in activation_codes if code.get('activationCodeId') is not None]
    
    return activation_code_ids if activation_code_ids else None

def renew_activation_code(subdomain, token, login, last_name, account_number, activation_code_id):
    url = f'https://{subdomain}.norago.tv/apex/v2/activationcodes/renew'
    
    data = {
        "auth": {
            "token": token,
            "login": login,
            "accountNumber": account_number,
            "lastName": last_name
        },
        "activationCodeId": activation_code_id
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    # Verificar se a resposta foi bem-sucedida
    if result.get('status', {}).get('code') == '0':
        return result
    else:
        print(f"Erro ao renovar o código de ativação {activation_code_id}.")
        return None

def renew_all_activation_codes(subdomain, token, login, last_name, account_number):
    # Obter todos os activationCodeId
    activation_code_ids = get_activation_codes(subdomain, token, login, last_name, account_number)
    
    if not activation_code_ids:
        print("Nenhum código de ativação encontrado.")
        return []
    
    link_codes = []
    
    for activation_code_id in activation_code_ids:
        # Renovar o código de ativação
        result = renew_activation_code(subdomain, token, login, last_name, account_number, activation_code_id)
        
        if result:
            # Extrair o linkCode da resposta
            link_code = result.get('result', {}).get('linkCode')
            if link_code:
                link_codes.append(link_code)

    return link_codes

def get_packages_info(subdomain, token, login):
    url = f'https://{subdomain}.norago.tv/apex/v2/subscriptions/get'
    
    data = {
        "auth": {
            "login": login,
            "token": token
        }
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    # Verificar se a resposta foi bem-sucedida
    if result.get('status', {}).get('code') != '0':
        print("Erro ao obter informações dos pacotes.")
        return None
    
    # Extrair subscriptionId e name de cada pacote
    packages = result.get('result', [])
    package_info = [{'subscriptionId': pkg.get('subscriptionId'), 'name': pkg.get('name')} for pkg in packages]
    
    return package_info

def get_network_info(subdomain, token, login):
    url = f'https://{subdomain}.norago.tv/apex/v2/networks/get'
    
    data = {
        "auth": {
            "token": token,
            "login": login
        },
        "pageRequest": {
            "page": 0
        }
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    # Verificar se a resposta foi bem-sucedida
    if result.get('status', {}).get('code') != '0':
        print("Erro ao obter informações da rede.")
        return None
    
    # Retornar a estrutura de dados com as informações da rede
    return result.get('result', {})

# Auth Setup
subdomain = os.getenv('subdomain')
token = os.getenv('token')
login = os.getenv('login')

# User Info Test Setup 
first_name = 'IhGabeZ'
last_name = 'Cord'
phone = '5099969999'
email = 'IhGabeZ@IhGabeZ.com'
account_number = 'SGO300230'

# Program Start 
def main_menu():
    while True:
        # Criar o Menu
        print("\n1. Create User")
        print("2. Search Subscriber")
        print("3. Make Payment")
        print("4. Get Subscriber Info")
        print("5. Remove Device")
        print("6. Delete Subscriber")
        print("7. Remove All Devices")
        print("8. Renew All Activation Codes")
        print("9. Get Packages Info")
        print("10. Get Network Info")
        print("11. Exit")
        
        choice = input("Escolha uma opção (1-11): ")
        
        if choice == '1':
            # Criar Usuário
            first_name, last_name, phone, email = input("Digite first_name last_name phone email: ").split()
            response = create_user(subdomain, token, login, first_name, last_name, phone, email)
            print(json.dumps(response, indent=4))
        
        elif choice == '2':
            # Buscar Assinante
            email = input("Digite email: ")
            response = search_subscriber(subdomain, token, login, email)
            print(json.dumps(response, indent=4))
        
        elif choice == '3':
            # Fazer Pagamento
            account_number, last_name, subscription_id = input("Digite account_number last_name subscription_id: ").split()
            response = make_payment(subdomain, token, login, account_number, last_name, subscription_id)
            print(json.dumps(response, indent=4))
        
        elif choice == '4':
            # Obter Informações do Assinante
            last_name, account_number = input("Digite last_name account_number: ").split()
            response = get_sub_info(subdomain, token, login, last_name, account_number)
            print(json.dumps(response, indent=4))
        
        elif choice == '5':
            # Remover Dispositivo
            last_name, account_number, device_number = input("Digite last_name account_number device_number: ").split()
            response = remove_device(subdomain, token, login, last_name, account_number, device_number)
            print(json.dumps(response, indent=4))
        
        elif choice == '6':
            # Excluir Assinante
            last_name, account_number = input("Digite last_name account_number: ").split()
            response = delete_subscriber(subdomain, token, login, last_name, account_number)
            print(json.dumps(response, indent=4))
        
        elif choice == '7':
            # Remover Todos os Dispositivos
            last_name, account_number = input("Digite last_name account_number: ").split()
            remove_all_devices(subdomain, token, login, last_name, account_number)
        
        elif choice == '8':
            # Renovar Todos os Códigos de Ativação
            last_name, account_number = input("Digite last_name account_number: ").split()
            link_codes = renew_all_activation_codes(subdomain, token, login, last_name, account_number)
            if link_codes:
                print("Link Codes:")
                for code in link_codes:
                    print(f"Code : {code}")
        
        elif choice == '9':
            # Obter Informações dos Pacotes
            response = get_packages_info(subdomain, token, login)
            print(json.dumps(response, indent=4))
        
        elif choice == '10':
            # Obter Informações da Rede
            response = get_network_info(subdomain, token, login)
            print(json.dumps(response, indent=4))
        
        elif choice == '11':
            # Sair
            break
        
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main_menu()