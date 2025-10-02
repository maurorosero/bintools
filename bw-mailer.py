#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bw-mailer.py: Script auxiliar para enviar emails para Bitwarden Send.

Este script recibe la configuración SMTP, la URL del send, los destinatarios
y la fecha de expiración para construir y enviar un email HTML.
"""

import smtplib
import json
import sys
import os
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email(smtp_config_str, url, recipients_str, expiration_text):
    """
    Construye y envía un email con la información del Bitwarden Send.
    """
    try:
        # Cargar configuración y argumentos
        smtp_config = json.loads(smtp_config_str)
        recipients = recipients_str.split(',')

        # --- Leer plantilla de email ---
        template_file = os.path.expanduser('~/secure/mail/email.bw.template')
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            # Plantilla por defecto (anti-spam) si el archivo no existe
            html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archivo Compartido</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
        .container { background: #ffffff; border: 1px solid #dddddd; border-radius: 8px; overflow: hidden; }
        .header { background: #007bff; color: #ffffff; padding: 20px; text-align: center; }
        .content { padding: 30px 25px; }
        .button { display: inline-block; background: #007bff; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
        .footer { padding: 20px 25px; text-align: center; color: #6c757d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>Archivo Compartido</h1></div>
        <div class="content">
            <p>Se ha compartido un archivo contigo de forma segura.</p>
            <p><a href="{{LINK}}" class="button">Acceder al Archivo</a></p>
            <p><strong>{{EXPIRES}}</strong></p>
            <p><small>Si no esperabas este archivo, por favor ignora este mensaje.</small></p>
        </div>
        <div class="footer"><p>Enviado de forma segura usando Bitwarden Send.</p></div>
    </div>
</body>
</html>
"""

        # --- Reemplazar variables en la plantilla ---
        html_content = html_content.replace('{{LINK}}', url)
        html_content = html_content.replace('{{DATE}}', datetime.now().strftime('%d/%m/%Y %H:%M'))

        if expiration_text and expiration_text != "None":
            html_content = html_content.replace('{{EXPIRES}}', f'El enlace expirará el {expiration_text}.')
        else:
            html_content = html_content.replace('{{EXPIRES}}', 'Este enlace no tiene fecha de expiración.')

        # --- Crear el objeto del mensaje ---
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Has recibido un archivo compartido de forma segura'
        msg['From'] = f"{smtp_config['smtp']['from']['name']} <{smtp_config['smtp']['from']['email']}>"
        msg['To'] = ', '.join(recipients)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # --- Conectar y enviar ---
        host = smtp_config['smtp']['host']
        port = smtp_config['smtp']['port']
        security = smtp_config['smtp']['security']
        username = smtp_config['smtp']['username']
        password = smtp_config['smtp']['password']

        server = None
        if security == 'tls':
            server = smtplib.SMTP(host, port)
            server.starttls()
        elif security == 'ssl':
            server = smtplib.SMTP_SSL(host, port)
        else:
            server = smtplib.SMTP(host, port)

        server.login(username, password)
        server.send_message(msg)
        server.quit()

        print("SUCCESS: Email enviado exitosamente.")
        return 0

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enviar email para Bitwarden Send.')
    parser.add_argument('--config', required=True, help='Configuración SMTP en formato JSON string.')
    parser.add_argument('--url', required=True, help='URL del Bitwarden Send.')
    parser.add_argument('--recipients', required=True, help='Lista de destinatarios separados por comas.')
    parser.add_argument('--expires', default="None", help='Texto de la fecha de expiración.')

    args = parser.parse_args()

    sys.exit(send_email(args.config, args.url, args.recipients, args.expires))
