#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import datetime
import pandas as pd
from collections import defaultdict
import os
import json
from typing import List, Dict, Any
import logging
from pathlib import Path
import argparse
import signal
import sys

# Configuración de rutas
DOCUMENTS_DIR = os.path.expanduser("~/Documents")
EMAILS_DIR = os.path.join(DOCUMENTS_DIR, "emails")
PROGRESS_FILE = os.path.join(EMAILS_DIR, 'progress.json')

# Crear directorio si no existe
os.makedirs(EMAILS_DIR, exist_ok=True)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EMAILS_DIR, 'email_manager.log')),
        logging.StreamHandler()
    ]
)

class EmailManager:
    def __init__(self, email_address: str, password: str, imap_server: str):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.mail = None
        self.categories = defaultdict(list)
        self.processed_emails = set()
        self.should_stop = False
        
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)
        
    def handle_interrupt(self, signum, frame):
        """Maneja la interrupción del programa"""
        logging.info("Interrupción detectada. Guardando progreso...")
        self.should_stop = True
        self.save_progress()
        self.close()
        sys.exit(0)
        
    def connect(self):
        """Conecta al servidor de correo"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            logging.info("Conexión exitosa al servidor de correo")
            return True
        except Exception as e:
            logging.error(f"Error al conectar: {str(e)}")
            return False

    def get_email_categories(self, email_data: Dict[str, Any]) -> List[str]:
        """Determina las categorías de un correo basado en su contenido"""
        categories = []
        
        # Categoría por fecha
        date = email_data.get('date')
        if date:
            try:
                email_date = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
                if email_date.year < 2015:
                    categories.append("antiguo")
            except:
                pass

        # Categoría por remitente
        from_addr = email_data.get('from', '').lower()
        if 'newsletter' in from_addr or 'marketing' in from_addr:
            categories.append("newsletter")
        if 'notification' in from_addr or 'alert' in from_addr:
            categories.append("notificaciones")

        # Categoría por asunto
        subject = email_data.get('subject', '').lower()
        if 'factura' in subject or 'invoice' in subject:
            categories.append("facturas")
        if 'confirmación' in subject or 'confirmation' in subject:
            categories.append("confirmaciones")

        return categories

    def load_progress(self):
        """Carga el progreso guardado"""
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, 'r') as f:
                    data = json.load(f)
                    self.processed_emails = set(data.get('processed_emails', []))
                    self.categories = defaultdict(list, data.get('categories', {}))
                logging.info(f"Progreso cargado: {len(self.processed_emails)} correos procesados")
                return True
        except Exception as e:
            logging.error(f"Error al cargar progreso: {str(e)}")
        return False

    def save_progress(self):
        """Guarda el progreso actual"""
        try:
            progress_data = {
                'processed_emails': list(self.processed_emails),
                'categories': dict(self.categories)
            }
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress_data, f)
            logging.info(f"Progreso guardado: {len(self.processed_emails)} correos procesados")
        except Exception as e:
            logging.error(f"Error al guardar progreso: {str(e)}")

    def analyze_emails(self, limit: int = None, force_init: bool = False):
        """Analiza los correos y los categoriza"""
        try:
            if not force_init:
                self.load_progress()
            
            self.mail.select('INBOX')
            _, messages = self.mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            if limit:
                email_ids = email_ids[-limit:]

            total_emails = len(email_ids)
            logging.info(f"Analizando {total_emails} correos...")

            for i, email_id in enumerate(email_ids):
                if self.should_stop:
                    break
                    
                email_id_str = email_id.decode()
                if email_id_str in self.processed_emails:
                    continue

                _, msg_data = self.mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                # Extraer información básica
                email_data = {
                    'id': email_id_str,
                    'date': email_message['date'],
                    'from': email_message['from'],
                    'subject': decode_header(email_message['subject'])[0][0],
                    'categories': []
                }

                # Determinar categorías
                email_data['categories'] = self.get_email_categories(email_data)
                
                # Agregar a las categorías correspondientes
                for category in email_data['categories']:
                    self.categories[category].append(email_data)

                self.processed_emails.add(email_id_str)
                
                if (i + 1) % 100 == 0:
                    logging.info(f"Procesados {i + 1}/{total_emails} correos")
                    self.save_progress()

            self.save_categories()
            logging.info("Análisis completado")
            return True

        except Exception as e:
            logging.error(f"Error al analizar correos: {str(e)}")
            return False

    def save_categories(self):
        """Guarda las categorías en un archivo JSON"""
        try:
            categories_file = os.path.join(EMAILS_DIR, 'email_categories.json')
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
            logging.info(f"Categorías guardadas exitosamente en {categories_file}")
        except Exception as e:
            logging.error(f"Error al guardar categorías: {str(e)}")

    def generate_report(self):
        """Genera un reporte de las categorías"""
        try:
            report_data = []
            for category, emails in self.categories.items():
                report_data.append({
                    'Categoría': category,
                    'Cantidad': len(emails),
                    'Ejemplo de remitente': emails[0]['from'] if emails else 'N/A'
                })

            report_file = os.path.join(EMAILS_DIR, 'email_report.csv')
            df = pd.DataFrame(report_data)
            df.to_csv(report_file, index=False)
            logging.info(f"Reporte generado exitosamente en {report_file}")
        except Exception as e:
            logging.error(f"Error al generar reporte: {str(e)}")

    def delete_emails_by_category(self, category: str, dry_run: bool = True):
        """Elimina correos por categoría"""
        try:
            if category not in self.categories:
                logging.error(f"Categoría {category} no encontrada")
                return False

            emails_to_delete = self.categories[category]
            logging.info(f"Preparando para eliminar {len(emails_to_delete)} correos de la categoría {category}")

            if dry_run:
                logging.info("Modo de prueba activado - no se eliminarán correos")
                return True

            for email_data in emails_to_delete:
                self.mail.store(email_data['id'], '+FLAGS', '\\Deleted')
            
            self.mail.expunge()
            logging.info(f"Correos de la categoría {category} eliminados exitosamente")
            return True

        except Exception as e:
            logging.error(f"Error al eliminar correos: {str(e)}")
            return False

    def close(self):
        """Cierra la conexión con el servidor de correo"""
        try:
            if self.mail:
                self.mail.close()
                self.mail.logout()
                logging.info("Conexión cerrada exitosamente")
        except Exception as e:
            logging.error(f"Error al cerrar conexión: {str(e)}")

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Gestor de correos electrónicos')
    parser.add_argument('--init', action='store_true', help='Iniciar análisis desde cero')
    parser.add_argument('--limit', type=int, help='Límite de correos a procesar')
    args = parser.parse_args()

    # Configuración
    EMAIL_ADDRESS = "tu_correo@dominio.com"
    PASSWORD = "tu_contraseña"
    IMAP_SERVER = "imap.tu_servidor.com"

    # Crear instancia del gestor de correos
    manager = EmailManager(EMAIL_ADDRESS, PASSWORD, IMAP_SERVER)

    # Conectar al servidor
    if not manager.connect():
        return

    try:
        # Analizar correos
        manager.analyze_emails(limit=args.limit, force_init=args.init)

        # Generar reporte
        manager.generate_report()

        # Ejemplo: eliminar correos de una categoría (modo de prueba)
        # manager.delete_emails_by_category("newsletter", dry_run=True)

    finally:
        manager.close()

if __name__ == "__main__":
    main() 