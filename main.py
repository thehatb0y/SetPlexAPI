import requests
import random
import json
import os
from rich import print_json
from colorama import init, Fore, Style
import time
from datetime import datetime

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

def get_full_info(subdomain, token, login):
    file_path = 'all_users.json'
    i = 0

    # Abrindo e lendo o arquivo JSON
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Dicionário para armazenar o novo JSON
    new_data = {}

    # Iterando sobre cada item na lista
    for item in data:
        last_name = item.get('lastName')
        account_number = item.get('accountNumber')
        i += 1
        
        if i % 15 == 0:
            time.sleep(1)
        
        try:
            # Obtendo a resposta para cada item
            response = get_sub_info(subdomain, token, login, last_name, account_number)
            
            # Extraindo as informações desejadas até "devices"
            result = response.get('result')
            
            if result is None:
                raise ValueError(f"Resposta inesperada: 'result' não encontrado para {account_number}")
            
            # Mantendo apenas informações até "devices"
            filtered_result = {}
            for key, value in result.items():
                filtered_result[key] = value
                if key == 'devices':
                    break
            
            # Adicionando o resultado ao novo dicionário com o "accountNumber" como chave
            new_data[account_number] = filtered_result
        
        except Exception as e:
            # Tratamento de erro: continue a execução e exiba o erro e o account_number
            print(f"Erro ao processar {account_number}: {e}")
            continue

    # Escrevendo o novo JSON em um arquivo
    with open('filtered_users.json', 'w') as new_file:
        json.dump(new_data, new_file, indent=4)

    print("Novo arquivo JSON criado: filtered_users.json")

def credit_time_to_everyone(subdomain, token, login, subscription_id):
    file_path = 'all_users_full.json'
    filtered_users = {}

    # Abrindo e lendo o arquivo JSON
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Iterando sobre cada item no JSON e filtrando por data
    for account_number, user_info in data.items():
        last_name = user_info.get('lastName')
        expiration_time = user_info.get('expirationTime')
        email = user_info.get('email')

        if expiration_time:
            date = datetime.strptime(expiration_time, "%Y-%m-%dT%H:%M:%SZ")
            if date.year == 2024 and date.month == 1 and date.day == 25:
                filtered_users[account_number] = {"lastName": last_name, "email": email}
                print(f"Account Number {account_number}, Last Name {last_name}, Expiration Time: {expiration_time}, Email {email}")
                make_payment(subdomain, token, login, account_number, last_name, subscription_id)


    # Contando o número total de usuários filtrados
    total_users = len(filtered_users)

    # Criando o dicionário final que inclui o total de usuários
    final_output = {
        "totalUsers": total_users,
        "users": filtered_users
    }

    # Salvando o novo JSON com os usuários filtrados e o total de usuários
    with open('receivedTimeUsers.json', 'w') as new_file:
        json.dump(final_output, new_file, indent=4)

def extractSubscriberFromDataX(day, month, year):
    file_path = 'all_users_full.json'
    filtered_users = {}

    # Abrindo e lendo o arquivo JSON
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Iterando sobre cada item no JSON e filtrando por data
    for account_number, user_info in data.items():
        last_name = user_info.get('lastName')
        expiration_time = user_info.get('expirationTime')
        email = user_info.get('email')

        if expiration_time:
            date = datetime.strptime(expiration_time, "%Y-%m-%dT%H:%M:%SZ")
            if date.year == 2024:# and date.month == 1: #and date.day == 28:
                filtered_users[account_number] = {"lastName": last_name, "email": email}
                print(f"Account Number {account_number}, Last Name {last_name}, Expiration Time: {expiration_time}, Email {email}")

    # Salvando os sobrenomes e emails em um arquivo de texto
    with open('receivedTimeUsers.txt', 'a') as file:
        for account_number, user_info in filtered_users.items():
            last_name = user_info.get('lastName')
            email = user_info.get('email')
            file.write(f"{last_name}\n{email}\n")

    # Contando o número total de usuários filtrados
    total_users = len(filtered_users)

    # Criando o dicionário final que inclui o total de usuários
    final_output = {
        "totalUsers": total_users,
        "users": filtered_users
    }

    # Salvando o novo JSON com os usuários filtrados e o total de usuários
    with open('receivedTimeUsers.json', 'w') as new_file:
        json.dump(final_output, new_file, indent=4)

# Auth Setup
subdomain = os.getenv('noraSub')
token = os.getenv('token')
login = os.getenv('login')

subID = "4SDBdAD5"

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
        print(Fore.YELLOW + "12. " + Fore.WHITE + "Get Everyone Full Info")
        print(Fore.YELLOW + "13. " + Fore.WHITE + "Credit Time to Every1")
        print(Fore.YELLOW + "14. " + Fore.WHITE + "Extract Subscriber from Data X")
        print(Fore.RED + "15. " + Fore.WHITE + "Exit")
        print(Style.RESET_ALL)
        
        choice = input(Fore.GREEN + "Options (1-14): " + Style.RESET_ALL)
        
        if choice == '1':
            # Criar Usuário
            os.system("cls")
            first_name, last_name, phone, email = input(Fore.MAGENTA + "Type First Name " + Fore.RESET + Fore.GREEN + "Last Name " + Fore.RESET + Fore.YELLOW + "Phone " + Fore.RESET + Fore.CYAN + "Email " + Fore.RESET).split()
            response = create_user(subdomain, token, login, first_name, last_name, phone, email)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")
        
        elif choice == '2':
            # Buscar Assinante
            email = input(Fore.CYAN + "Type Email " + Fore.RESET)
            response = search_subscriber(subdomain, token, login, email)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")
        
        elif choice == '3':
            # Fazer Pagamento
            os.system("cls")
            account_number, last_name, subscription_id = input(Fore.GREEN + "Type Account Number " + Fore.RESET + Fore.MAGENTA + "Last Name " + Fore.RESET + Fore.YELLOW + "Subscription ID " + Fore.RESET).split()
            response = make_payment(subdomain, token, login, account_number, last_name, subscription_id)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")
        
        elif choice == '4':
            os.system("cls")
            # Obter Informações do Assinante
            last_name, account_number = input(Fore.MAGENTA + "Type Last Name " + Fore.RESET + Fore.GREEN + "Account Number " + Fore.RESET).split()
            response = get_sub_info(subdomain, token, login, last_name, account_number)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")
        
        elif choice == '5':
            os.system("cls")
            # Remover Dispositivo
            last_name, account_number, device_number = input(Fore.MAGENTA + "Type Last Name " + Fore.RESET + Fore.GREEN + "Account Number " + Fore.RESET + Fore.YELLOW + "Device Number " + Fore.RESET).split()
            response = remove_device(subdomain, token, login, last_name, account_number, device_number)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")
        
        elif choice == '6':
            os.system("cls")
            # Excluir Assinante
            last_name, account_number = input(Fore.MAGENTA + "Type Last Name " + Fore.RESET + Fore.GREEN + "Account Number " + Fore.RESET).split()
            response = delete_subscriber(subdomain, token, login, last_name, account_number)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '7':
            os.system("cls")
            # Remover Todos os Dispositivos
            last_name, account_number = input(Fore.MAGENTA + "Type Last Name " + Fore.RESET + Fore.GREEN + "Account Number " + Fore.RESET).split()
            remove_all_devices(subdomain, token, login, last_name, account_number)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '8':
            os.system("cls")
            # Renovar Todos os Códigos de Ativação
            last_name, account_number = input(Fore.MAGENTA + "Type Last Name " + Fore.RESET + Fore.GREEN + "Account Number " + Fore.RESET).split()
            link_codes = renew_all_activation_codes(subdomain, token, login, last_name, account_number)
            if link_codes:
                print("Link Codes:")
                for code in link_codes:
                    print(f"Code : {code}")
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '9':
            os.system("cls")
            # Obter Informações dos Pacotes
            response = get_packages_info(subdomain, token, login)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '10':
            os.system("cls")
            # Obter Informações da Rede
            response = get_network_info(subdomain, token, login)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '11':
            os.system("cls")
            # Obter Informações da Rede
            response = search_all(subdomain, token, login)
            print_json_color(response)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '12':
            os.system("cls")
            get_full_info(subdomain, token, login)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '13':
            os.system("cls")
            credit_time_to_everyone(subdomain, token, login, subID)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '14':
            os.system("cls")
            day, month, year = input(Fore.CYAN + "Type DAY " + Fore.RESET + Fore.GREEN + "MONTH " + Fore.RESET + Fore.YELLOW + "YEAR " + Fore.RESET).split()
            extractSubscriberFromDataX(day, month, year)
            input(Fore.RED + "Press enter to continue")
            os.system("cls")

        elif choice == '15':
            break

        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main_menu()
