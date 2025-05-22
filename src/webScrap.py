import requests
from bs4 import BeautifulSoup
import json
import base64

# 🔐 Token de autenticação recebido por e-mail
AUTH_TOKEN = "T4IKHuKmLa9y5wiQz6gaXysxTrOM4hot"

# 🌐 URLs fornecidas na avaliação
SCRAPE_URL = "https://intern.aiaxuropenings.com/scrape/c102c692-7fb4-4c91-8bc4-08f28789cf4d"
MODEL_URL = "https://intern.aiaxuropenings.com/v1/chat/completions"
SUBMIT_URL = "https://intern.aiaxuropenings.com/api/submit-response"


def baixar_imagem():
    """Faz o scraping da página e baixa a imagem encontrada."""
    print("🔍 Buscando imagem na página...")
    response = requests.get(SCRAPE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tag = soup.find('img')

    if img_tag is None:
        raise Exception("❌ Nenhuma tag <img> encontrada na página!")

    img_src = img_tag['src']
    print(f"🌐 Conteúdo da tag src: {img_src[:50]}...")  # Mostra os primeiros caracteres

    nome_arquivo = 'imagem.jpg'

    if img_src.startswith('data:image'):  # Caso seja uma imagem em base64
        header, encoded = img_src.split(',', 1)
        imagem = base64.b64decode(encoded)
        with open(nome_arquivo, 'wb') as f:
            f.write(imagem)
        print(f"✅ Imagem em base64 salva como {nome_arquivo}!")

    elif img_src.startswith('http'):
        imagem = requests.get(img_src)
        imagem.raise_for_status()
        with open(nome_arquivo, 'wb') as f:
            f.write(imagem.content)
        print(f"✅ Imagem baixada de URL e salva como {nome_arquivo}!")

    else:
        raise Exception("❌ Formato de imagem não reconhecido!")

    return nome_arquivo

def enviar_imagem(caminho_imagem):
    try:
        with open(caminho_imagem, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "microsoft-florence-2-large",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": image_data_url},
                        {"type": "text", "text": "<DETAILED_CAPTION>"}
                    ]
                }
            ]
        }

        response = requests.post(
            MODEL_URL,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

        resposta_json = response.json()

        print("✅ Resposta do modelo recebida com sucesso!")
        print("🧠 Conteúdo da resposta JSON:")
        print(json.dumps(resposta_json, indent=4, ensure_ascii=False))  # Print bonito do JSON

        return resposta_json

    except requests.exceptions.HTTPError as e:
        print("❌ Erro na requisição HTTP:", e)
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        raise

    except Exception as e:
        print("❌ Erro inesperado:", e)
        raise

def enviar_resposta(resposta_json):
    """Submete a resposta JSON recebida do modelo para a plataforma da Axur."""
    print("📤 Enviando resposta para a plataforma da Axur...")
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(SUBMIT_URL, headers=headers, json=resposta_json)
    response.raise_for_status()

    print("✅ Resposta submetida com sucesso!")
    print("📨 Resposta da API:", response.text)


if __name__ == "__main__":
    try:
        caminho = baixar_imagem()
        resposta = enviar_imagem(caminho)
        enviar_resposta(resposta)
        print("🎯 Script executado com sucesso!")
    except Exception as e:
        print("❌ Ocorreu um erro durante a execução do script:", e)
