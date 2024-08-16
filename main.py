import requests
import random
import json
import os
from rich import print_json
from colorama import init, Fore, Style

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

def search_all(subdomain, token, login):
    url = f'https://{subdomain}.norago.tv/apex/v2/networks/subscribers/get'
    network_info = get_network_info(subdomain, token, login)
    networkID = network_info["content"][0]["id"]  # Extrai o networkID do retorno de get_network_info
    
    all_users = []  # Lista para armazenar todos os usuários de todas as páginas
    
    # Inicia a primeira requisição para obter o total de páginas
    page = 0
    payload = json.dumps({
        "auth": {
            "token": token,
            "login": login
        },
        "pageRequest": {
            "page": page
        },
        "networkId": networkID
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    # Verifica o total de páginas
    total_pages = data["result"]["totalPages"]
    
    # Loop sobre todas as páginas
    for page in range(total_pages):
        payload = json.dumps({
            "auth": {
                "token": token,
                "login": login
            },
            "pageRequest": {
                "page": page
            },
            "networkId": networkID
        })
        
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        # Adiciona os usuários da página atual à lista de todos os usuários
        all_users.extend(data["result"]["content"])
    
    # Salva todos os usuários em um arquivo JSON
    with open('all_users.json', 'w') as f:
        json.dump(all_users, f, indent=4)

    return f'Total de usuários coletados: {len(all_users)}'
    
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

def print_json_color(json_data):
    # A função print_json do rich cuida da formatação e coloração automaticamente.
    print_json(data=json_data)

# Auth Setup
subdomain = os.getenv('noraSub')
token = os.getenv('r2_token')
login = os.getenv('r2_login')

# EG 1 Month Package - CXFFH2VVA
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
        print(Fore.CYAN + Style.BRIGHT + "===== Menu Principal =====")
        print(Fore.YELLOW + "1. " + Fore.WHITE + "Create User")
        print(Fore.YELLOW + "2. " + Fore.WHITE + "Search Subscriber")
        print(Fore.YELLOW + "3. " + Fore.WHITE + "Make Payment")
        print(Fore.YELLOW + "4. " + Fore.WHITE + "Get Subscriber Info")
        print(Fore.YELLOW + "5. " + Fore.WHITE + "Remove Device")
        print(Fore.YELLOW + "6. " + Fore.WHITE + "Delete Subscriber")
        print(Fore.YELLOW + "7. " + Fore.WHITE + "Remove All Devices")
        print(Fore.YELLOW + "8. " + Fore.WHITE + "Renew All Activation Codes")
        print(Fore.YELLOW + "9. " + Fore.WHITE + "Get Packages Info")
        print(Fore.YELLOW + "10. " + Fore.WHITE + "Get Network Info")
        print(Fore.YELLOW + "11. " + Fore.WHITE + "Search/Save All")
        print(Fore.RED + "12. " + Fore.WHITE + "Exit")
        print(Style.RESET_ALL)
        
        choice = input(Fore.GREEN + "Escolha uma opção (1-12): " + Style.RESET_ALL)
        
        if choice == '1':
            # Criar Usuário
            first_name, last_name, phone, email = input("Digite first_name last_name phone email: ").split()
            response = create_user(subdomain, token, login, first_name, last_name, phone, email)
            print_json_color(response)
        
        elif choice == '2':
            # Buscar Assinante
            email = input("Digite email: ")
            response = search_subscriber(subdomain, token, login, email)
            print_json_color(response)
        
        elif choice == '3':
            # Fazer Pagamento
            account_number, last_name, subscription_id = input("Digite account_number last_name subscription_id: ").split()
            response = make_payment(subdomain, token, login, account_number, last_name, subscription_id)
            print_json_color(response)
        
        elif choice == '4':
            # Obter Informações do Assinante
            last_name, account_number = input("Digite last_name account_number: ").split()
            response = get_sub_info(subdomain, token, login, last_name, account_number)
            print_json_color(response)
        
        elif choice == '5':
            # Remover Dispositivo
            last_name, account_number, device_number = input("Digite last_name account_number device_number: ").split()
            response = remove_device(subdomain, token, login, last_name, account_number, device_number)
            print_json_color(response)
        
        elif choice == '6':
            # Excluir Assinante
            last_name, account_number = input("Digite last_name account_number: ").split()
            response = delete_subscriber(subdomain, token, login, last_name, account_number)
            print_json_color(response)
        
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
            print_json_color(response)
        
        elif choice == '10':
            # Obter Informações da Rede
            response = get_network_info(subdomain, token, login)
            print_json_color(response)

        elif choice == '11':
            # Obter Informações da Rede
            response = search_all(subdomain, token, login)
            print_json_color(response)

        elif choice == '12':
            # Sair
            break
        
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main_menu()
