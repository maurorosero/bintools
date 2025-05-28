# Guía Súper Fácil de SOPS (¡Para Guardar Secretos!)

<!-- PARSEABLE_METADATA_START
purpose: Proporcionar una guía completa y detallada sobre SOPS, sus características, configuración y uso, con un enfoque didáctico.
technology: SOPS, GPG, age, AWS KMS, GCP KMS, Azure Key Vault, HashiCorp Vault
status: Development
PARSEABLE_METADATA_END -->

<!-- CURRENT_VERSION_PLACEHOLDER -->

<!-- ¡Hola! Esta guía te enseñará a usar SOPS, una herramienta genial para guardar secretos a salvo. -->

<!-- TOC -->
<!-- Más adelante pondremos aquí un índice para encontrar las cosas fácil. -->

## 1. ¡Hola, SOPS! ¿Qué Haces?

Imagina que tienes un diario súper secreto donde escribes contraseñas, códigos mágicos (como los tokens de API) o cualquier cosa que no quieres que nadie más vea. Dejar ese diario abierto por ahí sería muy arriesgado, ¿verdad?

¡Aquí es donde entra SOPS! SOPS es como **una cerradura súper especial y mágica para tu diario secreto (o cualquier archivo con secretos)**.

### 1.1. ¿Qué tiene de especial esta cerradura SOPS?

¡SOPS tiene superpoderes!

*   **Bloqueo Inteligente**: No bloquea toda la página de tu diario. ¡Puede bloquear solo las palabras secretas que tú le digas! Así, puedes seguir viendo el resto de la página, pero las palabras importantes están a salvo.
*   **Usa Diferentes Llaves Mágicas**: SOPS no usa una sola llave. Puede usar diferentes tipos de llaves mágicas para cerrar la cerradura. Hay llaves personales (como las de un mago PGP o las nuevas llaves `age`), llaves guardadas en castillos mágicos en la nube (AWS, Google Cloud, Azure) o incluso llaves de una caja fuerte especial llamada Vault.
*   **Amigo de tu Mochila (Git)**: Puedes guardar tu diario cerrado con SOPS en tu mochila (tu repositorio Git) junto con tus otros cuadernos y nadie podrá leer los secretos, ¡pero tú sí podrás cuando lo necesites!
*   **Funciona con Notas Diferentes**: No importa si tu secreto está escrito en un papel especial YAML, JSON, o incluso en una nota rápida tipo `.env`. ¡SOPS puede cerrarlo!
*   **Recuerda Quién Cerró**: La cerradura SOPS guarda una pequeña nota que dice quién usó la llave mágica y cuándo.
*   **Editar Fácil**: Si quieres añadir un nuevo secreto rápido, SOPS tiene un truco para abrir la cerradura un poquito, dejarte escribir y volver a cerrarla enseguida.

### 1.2. ¿Cómo funciona esta magia?

SOPS es inteligente y sigue algunas reglas importantes:

*   **¡Primero la Seguridad!**: Usa magia muy fuerte y probada para que nadie pueda romper la cerradura fácilmente.
*   **Ver Dónde Está el Secreto**: Aunque no puedas leer la palabra secreta, puedes ver *dónde* está guardada en la página. ¡No es un borrón invisible!
*   **Fácil de Usar (¡Lo Intenta!)**: Poner cerraduras puede ser complicado, pero SOPS intenta que sea lo más fácil posible, como usar un candado normal.
*   **Tú Eliges la Llave**: Puedes escoger la llave mágica que mejor funcione para ti o para tu equipo.

## 2. ¡Consiguiendo la Herramienta Mágica SOPS!

Para usar SOPS, primero necesitas tener la herramienta en tu computadora. Es como conseguir tu propio juego de llaves mágicas.

### 2.1. Si usas Linux (como Ubuntu, Fedora...)

*   **La Forma Más Fácil (a veces)**: Busca si tu tienda de aplicaciones de Linux (`apt`, `dnf`, `yum`) tiene SOPS. ¡Quizás puedas instalarlo con un solo comando!
    ```bash
    # Para Ubuntu/Debian (prueba esto)
    # sudo apt update && sudo apt install sops
    # Para Fedora (prueba esto)
    # sudo dnf install sops
    ```
*   **La Forma Segura (¡Funciona Siempre!)**: Ve a la página de SOPS en internet ([Releases de SOPS en GitHub](https://github.com/getsops/sops/releases)). Baja el archivo que dice "linux" y que sea para tu compu (normalmente `amd64`). Luego, dale permiso para funcionar (`chmod +x nombre_del_archivo`) y muévelo a un lugar donde tu compu busque herramientas (`sudo mv nombre_del_archivo /usr/local/bin/sops`).
*   **Con Snap**: Si usas Snap, puedes probar: `sudo snap install sops`

### 2.2. Si usas macOS (la compu de la manzana)

*   **La Forma Más Fácil (¡Si tienes Homebrew!)**: Homebrew es como un ayudante para instalar cosas en Mac. Si lo tienes, solo escribe en la terminal:
    ```bash
    brew install sops
    ```
*   **La Otra Forma**: Ve a la página de SOPS ([Releases de SOPS en GitHub](https://github.com/getsops/sops/releases)). Baja el archivo que dice "darwin" (¡así le dicen a macOS!). Dale permiso (`chmod +x nombre_del_archivo`) y muévelo a `/usr/local/bin/sops` (`sudo mv nombre_del_archivo /usr/local/bin/sops`).

### 2.3. Si usas Windows

*   **La Forma Fácil**: Ve a la página de SOPS ([Releases de SOPS en GitHub](https://github.com/getsops/sops/releases)). Baja el archivo que termina en `.exe`. Guarda ese archivo `sops.exe` en una carpeta que tu computadora sepa que debe mirar para encontrar programas (una carpeta que esté en tu "Path").
*   **Con Ayudantes (Scoop o Chocolatey)**: Si usas herramientas como Scoop o Chocolatey, puedes instalarlo fácil:
```bash
    # Con Scoop
    # scoop install sops
    # Con Chocolatey
    # choco install sops
```

### 2.4. ¿Funcionó?

Abre tu terminal (la pantalla negra para escribir comandos) y escribe:
```bash
sops --version
```
Si te responde con un número de versión (como `sops 3.7.1`), ¡genial! ¡Ya tienes la herramienta SOPS!

**¡Ojo!** Tener la herramienta SOPS es el primer paso. Para que funcione de verdad, necesitas también las **llaves mágicas** (como GPG o acceso a las nubes). ¡De eso hablaremos ahora!

## 3. Las Piezas Clave de SOPS: Llaves Mágicas y Libros de Reglas

SOPS es genial, pero no funciona solo. Necesita dos cosas importantes:

1.  **Llaves Mágicas (Proveedores de Claves)**: Estas son las que hacen la verdadera magia de cerrar y abrir.
2.  **Un Libro de Reglas (`.sops.yaml`)**: Este libro le dice a SOPS *cómo* usar las llaves mágicas.

### 3.1. Las Diferentes Llaves Mágicas (Proveedores de Claves)

Piensa en SOPS como un guardián de secretos muy listo. SOPS tiene una pequeña llave especial para cada secreto que guarda (esta llave se llama DEK, ¡pero no te preocupes por el nombre!). Lo importante es que SOPS no deja esa pequeña llave por ahí tirada. ¡La guarda dentro de una **caja súper fuerte**!

Y para cerrar esa caja súper fuerte, SOPS usa una **Llave Mágica Maestra**. ¡Y puede usar diferentes tipos de Llaves Mágicas Maestras!

Estas son las más famosas:

*   **Llave Mágica Personal (PGP)**: Es como una llave de mago muy antigua y respetada. Tú tienes una parte secreta de la llave (la clave privada) y le das la parte pública a SOPS para que cierre la caja. Solo tú, con tu parte secreta, puedes pedirle a SOPS que abra la caja.
*   **Llave Mágica Nueva (`age`)**: Es como la llave PGP, pero más moderna y fácil de usar. También tienes una parte secreta y le das la parte pública a SOPS.
*   **Llave del Castillo en la Nube (AWS KMS)**: Imagina una caja fuerte gigante en el castillo de Amazon en la nube. SOPS le pide a este castillo que cierre la caja de la llave pequeña usando la magia de AWS. Solo los caballeros (usuarios o programas) con el permiso correcto de AWS pueden pedirle al castillo que abra la caja.
*   **Llave del Castillo de Google (GCP KMS)**: ¡Lo mismo, pero en el castillo de Google en la nube!
*   **Llave del Castillo de Microsoft (Azure Key Vault)**: ¡Y también funciona con el castillo de Microsoft Azure!
*   **Llave de la Caja Fuerte del Dragón (HashiCorp Vault)**: A veces, las empresas tienen su propia caja fuerte mágica (¡como un dragón guardián!) llamada Vault. SOPS puede pedirle a este dragón que cierre la caja de la llave pequeña.

¡Lo genial es que SOPS puede usar una o varias de estas llaves mágicas al mismo tiempo para cerrar la caja de la llave pequeña! Así, diferentes personas o sistemas pueden abrir el secreto si tienen la llave correcta.

### 3.2. El Libro de Reglas Mágicas (`.sops.yaml`)

¿Cómo sabe SOPS qué llave mágica usar? ¿Y cómo sabe qué palabras secretas cerrar en tu diario? ¡Lo lee en su **Libro de Reglas Mágicas**! Este libro es un archivo que se llama `.sops.yaml`.

Cuando le pides a SOPS que cierre un secreto, SOPS busca este libro de reglas en la misma carpeta donde está el secreto. Si no lo encuentra, busca en la carpeta de arriba, y así hasta que lo encuentre.

**¿Qué hay escrito en este libro de reglas?**

*   **Reglas Principales (`creation_rules`)**: ¡Esta es la parte más importante! Aquí escribes las reglas para cerrar secretos.
*   **¿Para Qué Diario es la Regla? (`path_regex`)**: Puedes escribir reglas diferentes para diferentes diarios (archivos) usando patrones especiales. Por ejemplo, una regla para todos los diarios que terminen en `.secret`.
*   **¿Qué Palabras Cerrar? (`encrypted_regex`)**: Le dices a SOPS qué tipo de palabras buscar para ponerles la cerradura mágica (ej. todas las palabras que se llamen `password` o `token`).
*   **¿Qué Palabras NO Cerrar? (`unencrypted_regex`)**: También puedes decirle qué palabras *no* debe cerrar nunca, aunque parezcan secretas.
*   **¿Qué Llaves Mágicas Usar? (¡La parte clave!)**: Aquí es donde le dices a SOPS: "Para cerrar este tipo de diario, usa la Llave Mágica Personal de Ana Y la Llave del Castillo de AWS". (Aquí escribirías los nombres técnicos de las llaves, como la huella PGP de Ana o el ARN de la llave de AWS). **(¡Veremos cómo escribir esto en el Capítulo 4!)**
*   **¿Grupos de Llaves? (`key_groups`)**: ¡A veces necesitas varias llaves juntas! Esta parte del libro es para reglas más avanzadas. ¡Le dedicaremos un capítulo entero (el Capítulo 5) porque es súper interesante!

**Un Ejemplo de una Página del Libro de Reglas:**

```yaml
# Libro de Reglas Mágicas para SOPS
creation_rules:
  # Regla número 1: Para los diarios secretos de producción...
  - path_regex: 'produccion/.*\.yaml' # ...que estén en la carpeta "produccion" y terminen en .yaml
    # ...usa estas dos llaves mágicas PGP para cerrarlos:
    pgp: 'LLAVE_MAGICA_DE_ADMIN1,LLAVE_MAGICA_DE_ADMIN2'
    # ...y cierra solo las palabras secretas bajo "datos_secretos":
    encrypted_regex: ^(datos_secretos)$
```

¡Este libro de reglas es muy importante! Sin él, SOPS no sabría cómo cerrar tus secretos correctamente y de forma segura cada vez. Tendrías que decirle qué llave usar cada vez que cierras algo, ¡y eso sería un lío!

Ahora que ya sabes qué es SOPS, cómo conseguirlo y cuáles son sus piezas clave (¡nunca mejor dicho!), en los siguientes capítulos veremos cómo escribir las reglas para cada tipo de llave mágica y cómo usar los comandos de SOPS.

---
<!-- Siguiente sección: ## 4. Escribiendo Reglas para las Llaves Mágicas... -->
## 4. Escribiendo en el Libro de Reglas: ¡Diciéndole a SOPS Qué Llave Usar!

Recuerda nuestro Libro de Reglas Mágicas (`.sops.yaml`). Dentro de él, en la parte llamada `creation_rules`, es donde escribimos las instrucciones para SOPS. ¡La instrucción más importante es decirle **qué Llave Mágica Maestra usar** para cerrar la caja fuerte donde se guarda la llave pequeña del secreto!

Vamos a aprender cómo escribir estas instrucciones para cada tipo de Llave Mágica.

### 4.1. ¿Cómo se escribe una regla?

Cada regla es como una receta. Le dice a SOPS:
1.  **¿Para qué diarios secretos es esta receta?** (Usando `path_regex`, como vimos antes).
2.  **¿Qué Llave Mágica (o llaves) hay que usar?** (¡Esto es lo que veremos ahora!).

### 4.2. Usando la Llave Mágica Personal (PGP)

Esta es la llave del mago, ¡la que solo tú (o las personas que tú elijas) tienen la parte secreta para abrir!

*   **Código Secreto en el Libro**: Para decirle a SOPS que use esta llave, escribes `pgp:` en tu regla.
*   **¿Qué necesita SOPS?**: Necesita el "número de serie" súper largo y secreto de la llave PGP (esto se llama **huella digital** o *fingerprint*). Es como la combinación única de esa llave.
*   **Ejemplo en el Libro de Reglas**:
    ```yaml
    creation_rules:
      # Regla para los secretos en archivos .env
      - path_regex: '\.env.secret$'
        # ¡Usa estas llaves PGP!
        pgp: 'NUMERO_SECRETO_LARGO_DE_ANA,NUMERO_SECRETO_LARGO_DE_JUAN'
    ```
    (Aquí, reemplazas `NUMERO_SECRETO_LARGO_...` con las huellas reales).
*   **¿Cómo funciona?**: SOPS busca las llaves públicas que coinciden con esos números secretos en tu llavero GPG (una cajita donde guardas tus llaves PGP). Usa esas llaves públicas para cerrar la caja fuerte del secreto. Para abrirla, ¡necesitas la llave privada que hace juego con uno de esos números secretos!
*   **Pistas Secretas (Variables de Entorno)**:
    *   A veces, puedes darle una pista a SOPS escribiendo `SOPS_PGP_FP=NUMERO_SECRETO1,NUMERO_SECRETO2` como un mensaje secreto en tu computadora (variable de entorno).
    *   Si tus llaves PGP no están en la carpeta normal (`~/.gnupg`), puedes decirle a SOPS dónde buscar con la pista `GNUPGHOME=/ruta/a/tus/llaves`.

### 4.3. Usando la Llave Mágica Nueva (`age`)

Esta llave es como la PGP, ¡pero más moderna y fácil de manejar!

*   **Código Secreto en el Libro**: Escribes `age:`.
*   **¿Qué necesita SOPS?**: Necesita la clave pública `age` de las personas que podrán abrir el secreto. Estas claves empiezan con `age1...` y son más cortitas que las de PGP.
*   **Ejemplo en el Libro de Reglas**:
    ```yaml
    creation_rules:
      # Regla para los secretos de la app "juego"
      - path_regex: 'juego/.*\.yaml$'
        # ¡Usa estas llaves age!
        age: 'age1clavepublicadeana...,age1clavepublicadejuan...'
    ```
*   **¿Cómo funciona?**: Muy parecido a PGP. SOPS usa las claves públicas `age` para cerrar la caja fuerte. Para abrirla, necesitas la clave privada `age` que corresponde a una de esas claves públicas.
*   **Pistas Secretas (Variables de Entorno)**:
    *   Puedes dar la lista de claves públicas `age` con `SOPS_AGE_RECIPIENTS=...` o en un archivo con `SOPS_AGE_RECIPIENTS_FILE=...`.
    *   Para abrir, puedes darle a SOPS tu clave privada `age` directamente con `SOPS_AGE_KEY=...` (¡cuidado, menos seguro!) o, mejor aún, decirle dónde está el archivo con tu clave privada usando `SOPS_AGE_KEY_FILE=/ruta/a/tu/llave/privada.txt`.

### 4.4. Usando la Llave del Castillo en la Nube (AWS KMS)

¡Aquí le pedimos ayuda al gran castillo de Amazon Web Services (AWS) para guardar nuestra llave secreta!

*   **Código Secreto en el Libro**: Escribes `kms:`.
*   **¿Qué necesita SOPS?**: Necesita la "dirección mágica" exacta de la caja fuerte que quieres usar dentro del castillo de AWS. Esta dirección se llama **ARN**.
*   **Ejemplo en el Libro de Reglas**:
    ```yaml
    creation_rules:
      # Regla para los secretos de producción
      - path_regex: 'produccion/.*'
        # ¡Usa estas cajas fuertes del castillo AWS!
        kms:
          # Caja fuerte principal en la región Este de USA
          - 'arn:aws:kms:us-east-1:111122223333:key/DIRECCION_CAJA_FUERTE_1'
          # También una caja de respaldo en Europa, con reglas especiales
          - arn: 'arn:aws:kms:eu-west-1:111122223333:key/DIRECCION_CAJA_FUERTE_2'
            aws_profile: 'guardia_secreto' # Usa el disfraz de "guardia_secreto"
            role: 'arn:aws:iam::111122223333:role/RolParaAbrirSecretos' # Y pide permiso como este rol especial
            encryption_context: # Ponle estas etiquetas mágicas a la caja
              ambiente: produccion
              app: mi_juego_genial
    ```
*   **¿Cómo funciona?**: SOPS va al castillo de AWS y le dice: "¡Oye, AWS! Guarda esta llave pequeña en la caja fuerte con la dirección mágica `DIRECCION_CAJA_FUERTE_1`." AWS lo hace usando su propia magia súper segura. Para abrirla, tu computadora (o tú) necesita tener un permiso especial de AWS para usar esa caja fuerte.
*   **Pistas Secretas (Variables de Entorno de AWS)**: SOPS es listo y puede usar las pistas secretas normales de AWS que quizás ya tengas en tu computadora (como `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_PROFILE`, `AWS_REGION`) para saber cómo hablar con el castillo de AWS.

### 4.5. Usando la Llave del Castillo de Google (GCP KMS)

¡Igual que con AWS, pero ahora le pedimos ayuda al castillo de Google Cloud (GCP)!

*   **Código Secreto en el Libro**: Escribes `gcp_kms:`.
*   **¿Qué necesita SOPS?**: Necesita la "dirección mágica" de la caja fuerte dentro del castillo de Google. Se parece un poco a una dirección de página web larga (`projects/.../locations/.../keyRings/.../cryptoKeys/...`).
*   **Ejemplo en el Libro de Reglas**:
    ```yaml
    creation_rules:
      - gcp_kms:
          # ¡Usa esta caja fuerte del castillo de Google!
          - 'projects/mi-proyecto-gcp/locations/global/keyRings/mi-llavero/cryptoKeys/mi-llave-sops'
    ```
*   **¿Cómo funciona?**: SOPS le pide al castillo de Google que guarde la llave pequeña en la caja fuerte especificada. Para abrirla, necesitas tener permiso de Google Cloud para usar esa caja fuerte.
*   **Pistas Secretas (Variables de Entorno de GCP)**: La pista más importante es `GOOGLE_APPLICATION_CREDENTIALS`. Esta pista le dice a SOPS dónde encontrar un archivo especial (una llave de cuenta de servicio) que le da permiso para hablar con el castillo de Google.

### 4.6. Usando la Llave del Castillo de Microsoft (Azure Key Vault)

¡También podemos usar el castillo de Microsoft Azure!

*   **Código Secreto en el Libro**: Escribes `azure_keyvault:`.
*   **¿Qué necesita SOPS?**: Necesita la "dirección web" de la caja fuerte (la llave) dentro del castillo de Azure. Se parece a `https://nombre-del-castillo.vault.azure.net/keys/nombre-de-la-llave/version-secreta`.
*   **Ejemplo en el Libro de Reglas**:
    ```yaml
    creation_rules:
      - azure_keyvault:
          # ¡Usa esta caja fuerte del castillo de Azure!
          - 'https://mi-castillo-azure.vault.azure.net/keys/llave-para-sops/NUMERO_VERSION_SECRETO'
    ```
*   **¿Cómo funciona?**: SOPS le pide al castillo de Azure que guarde la llave pequeña usando la caja fuerte (llave) indicada. Para abrirla, necesitas tener permiso en Azure para usar esa llave específica.
*   **Pistas Secretas (Variables de Entorno de Azure)**: SOPS busca pistas como `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` y `AZURE_CLIENT_SECRET` para saber quién eres y si tienes permiso para entrar al castillo de Azure.

### 4.7. Usando la Llave de la Caja Fuerte del Dragón (HashiCorp Vault)

¡Si tienes tu propia caja fuerte mágica llamada Vault, SOPS también puede usarla!

*   **Código Secreto en el Libro**: Escribes `hc_vault:`.
*   **¿Qué necesita SOPS?**: Necesita saber el "nombre de la cerradura especial" dentro de la caja fuerte del Dragón Vault que debe usar (por ejemplo, `transit/keys/mi-llave-super-segura`).
*   **Ejemplo en el Libro de Reglas**:
    ```yaml
    creation_rules:
      - hc_vault:
          # Pídele al Dragón Vault que use la cerradura "mi-llave-app"
          # que está en el pasillo "transit_apps"
          - transit_path: 'transit_apps'
            key_name: 'mi-llave-app'
          # También usa esta otra cerradura más simple
          - 'transit/keys/llave_compartida'
    ```
*   **¿Cómo funciona?**: SOPS le envía la llave pequeña al Dragón Vault y le dice: "¡Guárdala usando la cerradura `mi-llave-app`!". El Dragón lo hace y le devuelve la llave pequeña cerrada. Para abrirla, necesitas un permiso especial (un token) del Dragón Vault que te deje usar esa cerradura.
*   **Pistas Secretas (Variables de Entorno de Vault)**: SOPS busca la dirección del castillo del Dragón (`VAULT_ADDR`) y tu permiso especial (`VAULT_TOKEN`) en las pistas secretas de tu computadora.

¡Uf! Son muchas llaves mágicas, ¿verdad? No tienes que usarlas todas. Solo elige la(s) que tenga(n) sentido para ti y para cómo guardas tus cosas.

En el próximo capítulo, veremos algo súper emocionante: ¡cómo combinar estas llaves para que varias personas necesiten juntar sus llaves para abrir un secreto!

---

## 5. ¡Abriendo Cofres con Múltiples Llaves! (Grupos de Claves y el Umbral Mágico)

¡Prepárate para uno de los trucos más geniales de SOPS! A veces, no quieres que una sola Llave Mágica pueda abrir tu secreto. Quizás necesitas que **dos amigos usen sus llaves al mismo tiempo**, o quieres que funcione la **llave del Mago O la llave del Castillo en la Nube**. ¡SOPS puede hacer esto usando **Grupos de Claves (`key_groups`)** y un número mágico llamado **Umbral de Shamir (`shamir_threshold`)**!

Imagina que en lugar de cerrar la caja fuerte de la llave pequeña con una sola Llave Maestra, ¡SOPS puede usar **cofres especiales**!

### 5.1. ¿Qué es un Grupo de Claves (`key_group`)? (¡Un Cofre Especial!)

Piensa en cada `key_group` como un **cofre del tesoro mágico**. Puedes tener uno o varios de estos cofres para proteger la llave pequeña de tu secreto.

La regla es: si puedes abrir **AL MENOS UNO** de los cofres, ¡puedes abrir el secreto!

### 5.2. ¿Qué Llaves Mágicas puedes poner en un Cofre?

¡Dentro de cada cofre (`key_group`), puedes poner una mezcla de tus Llaves Mágicas favoritas!

*   Llaves Mágicas Personales (PGP)
*   Llaves Mágicas Nuevas (age)
*   Llaves del Castillo en la Nube (AWS KMS, GCP KMS, Azure Key Vault)
*   ¡Incluso la Llave del Dragón Vault!

Puedes poner una sola llave en un cofre, o poner varias llaves diferentes juntas.

### 5.3. El Número Mágico: `shamir_threshold` (¡Cuántas Llaves Necesitas!)

Aquí viene la parte divertida. Para CADA cofre (`key_group`), puedes decidir **cuántas de las llaves que pusiste DENTRO de ESE cofre son necesarias para abrirlo**. ¡Ese es el número mágico `shamir_threshold`!

*   **Si `shamir_threshold: 1`**: ¡Significa que CUALQUIERA de las llaves dentro de ese cofre puede abrirlo! Es como un cofre con muchas cerraduras diferentes, pero solo necesitas usar una.
*   **Si `shamir_threshold: 2`**: ¡Significa que necesitas usar **DOS** llaves diferentes de las que están dentro de ese cofre para abrirlo! No basta con una sola.
*   **Si `shamir_threshold: 3`**: ¡Necesitas **TRES** llaves diferentes de ese cofre!

¡Este número mágico usa un truco matemático súper inteligente llamado "Compartición de Secretos de Shamir" que divide el secreto de cómo abrir la caja fuerte en varias piezas, y necesitas suficientes piezas (llaves) para juntarlo de nuevo!

### 5.4. ¡Veamos los Cofres en Acción! (Ejemplos)

Vamos a ver cómo se escribe esto en nuestro Libro de Reglas (`.sops.yaml`):

**Ejemplo 1: El Cofre Personal (Solo Merlín)**
```yaml
creation_rules:
  - path_regex: 'secretos_de_merlin/.*'
    key_groups: # Abrimos la lista de cofres
      # Cofre 1: Solo para Merlín
      - pgp: ['NUMERO_SECRETO_DE_MERLIN'] # Llave PGP de Merlín
        shamir_threshold: 1 # Solo se necesita 1 llave (la de Merlín)
```
*   **Explicación**: Hay un solo cofre. Dentro hay una llave PGP (la de Merlín). Se necesita 1 llave para abrirlo. ¡Solo Merlín puede abrir este secreto!

**Ejemplo 2: El Cofre de los Dos Caballeros (Arturo Y Lancelot)**
```yaml
creation_rules:
  - path_regex: 'tesoro_real/.*'
    key_groups:
      # Cofre 1: Necesita a los dos caballeros
      - pgp:
          - 'NUMERO_SECRETO_ARTURO' # Llave de Arturo
          - 'NUMERO_SECRETO_LANCELOT' # Llave de Lancelot
        shamir_threshold: 2 # ¡Se necesitan 2 llaves para abrir este cofre!
```
*   **Explicación**: Hay un solo cofre, pero tiene dos llaves PGP dentro. Como el número mágico es 2, se necesitan **AMBAS** llaves (la de Arturo Y la de Lancelot) para abrir el secreto. ¡Ninguno puede hacerlo solo!

**Ejemplo 3: El Cofre Flexible (El Mago O el Castillo en la Nube)**
```yaml
creation_rules:
  - path_regex: 'planes_secretos/.*'
    key_groups:
      # Cofre 1: El Mago Gandalf puede abrirlo solo
      - pgp: ['NUMERO_SECRETO_GANDALF']
        shamir_threshold: 1 # Solo se necesita la llave de Gandalf

      # Cofre 2: O, el Castillo de AWS puede abrirlo solo
      - kms: ['ARN_DEL_CASTILLO_AWS']
        shamir_threshold: 1 # Solo se necesita la llave de AWS
```
*   **Explicación**: ¡Aquí tenemos **DOS** cofres (`key_groups`) diferentes! El primero solo necesita la llave PGP de Gandalf. El segundo solo necesita la llave del Castillo de AWS. Como solo necesitas poder abrir **UNO** de los cofres, significa que **O Gandalf O el Castillo de AWS** pueden abrir el secreto.

**Ejemplo 4: El Consejo de los Tres (¡Necesitamos a 2 de ellos!)**
```yaml
creation_rules:
  - path_regex: 'mapa_del_tesoro\.yaml'
    key_groups:
      # Cofre 1: El Consejo necesita estar de acuerdo
      - pgp: ['NUMERO_SECRETO_MAGO_1'] # Llave del Mago 1
        age: ['age1llavenuevadelamaga2...'] # Llave Nueva de la Maga 2
        azure_keyvault: ['URL_CASTILLO_AZURE_GUARDIAN3'] # Llave del Castillo Azure del Guardián 3
        shamir_threshold: 2 # ¡Se necesitan 2 CUALESQUIERA de estas 3 llaves!
```
*   **Explicación**: ¡Este es genial! Hay un solo cofre, pero con tres llaves mágicas diferentes dentro (PGP, age y Azure). Como el número mágico es 2, necesitas juntar **CUALESQUIERA DOS** de esas tres llaves para abrir el secreto. Por ejemplo:
    *   El Mago 1 y la Maga 2 juntos pueden abrirlo.
    *   El Mago 1 y el Guardián 3 (con su llave Azure) juntos pueden abrirlo.
    *   La Maga 2 y el Guardián 3 juntos pueden abrirlo.
    *   ¡Pero ninguno de ellos puede abrirlo solo!

### 5.5. ¿Por Qué Usar Estos Cofres Mágicos (`key_groups`)?

Usar `key_groups` y el número mágico `shamir_threshold` te da superpoderes:

*   **¡Más Seguridad!**: Para secretos súper importantes, puedes hacer que se necesiten varias personas (o sistemas) para abrirlos. Si alguien pierde su llave, ¡el secreto sigue a salvo!
*   **¡Más Flexibilidad!**: Puedes decidir quién puede abrir el secreto de diferentes maneras. Quizás los humanos usan sus llaves personales (PGP/age) y los programas usan las llaves de los castillos en la nube (KMS/Azure/GCP).
*   **Trabajo en Equipo**: Puedes asegurarte de que ciertas acciones necesiten la aprobación (las llaves) de más de una persona.

¡Jugar con los `key_groups` y el `shamir_threshold` es una de las partes más poderosas de SOPS para construir sistemas seguros y colaborativos!

---

## 6. ¡SOPS para Equipos! Guardando Secretos Juntos

SOPS es genial para guardar tus propios secretos, pero ¿qué pasa cuando trabajas en un equipo? ¡Imaginen que están construyendo un castillo de LEGO juntos y necesitan compartir las instrucciones secretas de las partes más difíciles!

No querrías simplemente dejar las instrucciones secretas a la vista de todos, ni tampoco darle una copia de tu llave secreta personal a cada amigo (¡eso no es seguro!). SOPS tiene trucos especiales para que los equipos puedan usar secretos de forma segura.

### 6.1. El Problema: ¿Cómo Compartimos Secretos Sin Peligro?

Si cada miembro del equipo (llamémoslos Ana, Ben y Carla) necesita usar la misma contraseña secreta para el WiFi del castillo, ¿cómo lo hacemos?

*   **Idea Mala 1**: Escribir la contraseña en un papel y dejarlo en la mesa (¡como guardar el secreto en Git sin SOPS!). Cualquiera podría verlo.
*   **Idea Mala 2**: Ana cierra el secreto con su Llave Mágica Personal PGP y le da una copia de *su* llave secreta a Ben y Carla. ¡Ahora Ben y Carla podrían abrir *todos* los secretos de Ana! ¡Muy mal!

**La Solución SOPS**: ¡Usamos las Llaves Públicas de todos!

### 6.2. El Truco Principal: ¡Muchas Llaves Públicas en el Libro de Reglas!

La forma más común y sencilla de trabajar en equipo con SOPS es: **¡cada persona usa su propia Llave Mágica Personal (PGP o age)!**

1.  **Cada Amigo Crea su Llave**: Ana, Ben y Carla crean cada uno su propia Llave Mágica Personal (PGP o age) y guardan muy bien su parte secreta (la clave privada).
2.  **Comparten la Parte Pública**: Cada uno comparte la parte pública de su llave (la que no es secreta) con el equipo.
3.  **Escribimos en el Libro de Reglas (`.sops.yaml`)**: En el Libro de Reglas, escribimos una regla que dice: "¡Para cerrar este secreto, usa la llave pública de Ana **Y** la llave pública de Ben **Y** la llave pública de Carla!".

**Ejemplo en el Libro de Reglas (con PGP):**
```yaml
creation_rules:
  - path_regex: 'secretos_del_equipo/.*'
    # ¡Cierra esto para que Ana, Ben O Carla puedan abrirlo!
    pgp: 'NUMERO_SECRETO_ANA,NUMERO_SECRETO_BEN,NUMERO_SECRETO_CARLA'
    # (Usamos sus huellas PGP aquí)
```

**¿Cómo funciona?**
*   **Para Cerrar (Encriptar)**: SOPS lee la regla, toma la llave pública de Ana, la de Ben y la de Carla, y cierra la caja fuerte de la llave pequeña del secreto de tal manera que *cualquiera* de ellos pueda abrirla después.
*   **Para Abrir (Desencriptar)**:
    *   Si Ana quiere abrir el secreto, usa su Llave Mágica Personal (su clave privada PGP). ¡Funciona!
    *   Si Ben quiere abrirlo, usa su propia llave. ¡Funciona!
    *   Si Carla quiere abrirlo, usa la suya. ¡Funciona!
    *   ¡Pero alguien que no sea Ana, Ben o Carla no puede abrirlo porque no tiene ninguna de las llaves correctas!

**¿Qué pasa si alguien se une o se va del equipo?**
*   **Nuevo Amigo (David se une)**:
    1.  David crea su llave PGP y comparte su número secreto (huella pública).
    2.  Actualizamos el Libro de Reglas (`.sops.yaml`) añadiendo la huella de David a la lista `pgp:`.
    3.  Alguien que ya tenga acceso (Ana, Ben o Carla) ejecuta un comando mágico especial: `sops updatekeys <archivo_secreto.sops.yaml>`. ¡Esto vuelve a cerrar el secreto para que David también pueda abrirlo! (Hablaremos más de `updatekeys` en el Capítulo 8).
*   **Amigo que se va (Carla se va)**:
    1.  Actualizamos el Libro de Reglas quitando la huella de Carla de la lista `pgp:`.
    2.  Alguien que todavía esté en el equipo (Ana o Ben) ejecuta `sops updatekeys <archivo_secreto.sops.yaml>`. ¡Esto vuelve a cerrar el secreto para que Carla ya NO pueda abrirlo!

¡Este método es genial porque nadie comparte su llave secreta personal!

### 6.3. Usando los Cofres Mágicos (`key_groups`) para Equipos

¡Podemos usar los cofres especiales (`key_groups`) que aprendimos en el capítulo anterior para hacer cosas aún más interesantes en equipo!

*   **¿Necesitamos que DOS personas aprueben?**: Imaginen que para lanzar los fuegos artificiales del castillo, se necesita que al menos dos caballeros (Arturo y Lancelot) usen sus llaves PGP al mismo tiempo.
    ```yaml
    creation_rules:
      - path_regex: 'lanzar_fuegos_artificiales.secret'
        key_groups:
          - pgp: ['LLAVE_ARTURO', 'LLAVE_LANCELOT', 'LLAVE_PERCEVAL']
            shamir_threshold: 2 # ¡Necesitamos 2 de estos 3 caballeros!
    ```
*   **¿El Líder O dos Miembros del Equipo?**: Quizás el Rey (Admin) puede abrir el cofre del tesoro él solo, O se necesita que dos de los Príncipes (Developers) lo hagan juntos.
    ```yaml
    creation_rules:
      - path_regex: 'cofre_del_tesoro.yaml'
        key_groups:
          # Opción 1: El Rey solo
          - pgp: ['LLAVE_DEL_REY']
            shamir_threshold: 1
          # Opción 2: Dos Príncipes juntos
          - pgp: ['LLAVE_PRINCIPE_1', 'LLAVE_PRINCIPE_2', 'LLAVE_PRINCIPE_3']
            shamir_threshold: 2
    ```

¡Los `key_groups` nos dan mucha flexibilidad para decidir quién puede abrir qué secretos y bajo qué condiciones!

### 6.4. ¡Dejando que los Castillos en la Nube o el Dragón Vault Ayuden!

Si tu equipo trabaja mucho con los castillos en la nube (AWS, GCP, Azure) o con la caja fuerte del Dragón Vault, ¡puedes usarlos para manejar el acceso!

En lugar de darle a cada persona una llave PGP, puedes configurar SOPS para que use una Llave Mágica del Castillo (una clave KMS o de Vault). Luego, en lugar de darle llaves SOPS a la gente, les das **permisos** en AWS, GCP, Azure o Vault.

*   **¿Cómo funciona?**: Si Ana tiene permiso en AWS para usar la caja fuerte `DIRECCION_CAJA_FUERTE_1`, y SOPS usa esa caja fuerte para cerrar el secreto, ¡Ana podrá abrirlo! Ben, que no tiene permiso en AWS, no podrá.
*   **Ventajas**: Puede ser más fácil manejar permisos en la nube o en Vault para equipos grandes, especialmente cuando la gente entra y sale del equipo. Simplemente les das o les quitas el permiso en la plataforma (AWS, GCP, etc.), y no necesitas cambiar el Libro de Reglas de SOPS (`.sops.yaml`) ni ejecutar `sops updatekeys` tan a menudo.
*   **Desventajas**: Dependes más de la configuración de la nube o de Vault.

¡Puedes incluso combinar llaves personales (PGP/age) con llaves de los castillos en la nube usando `key_groups`!

### 6.5. El Libro de Reglas (`.sops.yaml`) en la Mochila del Equipo (Git)

Cuando trabajas en equipo, el Libro de Reglas (`.sops.yaml`) es muy importante y todos necesitan usar el mismo.

*   **¡Guárdalo en la mochila Git!**: La mejor idea es guardar el archivo `.sops.yaml` en la misma mochila (repositorio Git) donde guardas el código del proyecto y los secretos cerrados con SOPS.
*   **¿Cambios en las Reglas? ¡Con cuidado!**: Si alguien necesita cambiar las reglas (por ejemplo, añadir la llave de un nuevo amigo), debería hacerlo con cuidado, quizás pidiendo a otros que revisen el cambio antes de guardarlo en la mochila Git (¡como hacer un Pull Request!).

### 6.6. Consejos para Equipos que usan SOPS

*   **Hablen Claro**: Asegúrense de que todos en el equipo sepan cómo se usan las Llaves Mágicas y el Libro de Reglas.
*   **Plan para Nuevos Amigos**: Tengan un plan claro para cuando alguien nuevo se une al equipo (cómo crear su llave, cómo añadirla al Libro de Reglas y actualizar los secretos).
*   **Plan para Despedidas**: Igualmente, tengan un plan para cuando alguien se va (cómo quitar su llave del Libro de Reglas y actualizar los secretos para que ya no pueda abrirlos).
*   **Revisen las Llaves**: De vez en cuando, revisen quién tiene acceso a qué secretos y si las llaves siguen siendo las correctas.

¡Usar SOPS en equipo es como tener un sistema secreto compartido que es seguro y fácil de manejar si todos siguen las reglas!

---

## 7. ¡Usando la Varita Mágica! Los Comandos de SOPS

Ya tienes la herramienta SOPS, sabes de las Llaves Mágicas y del Libro de Reglas (`.sops.yaml`). ¡Ahora vamos a aprender a usar la "varita mágica" de SOPS! Estos son los comandos que escribes en la terminal para hacer la magia.

### 7.1. Poner la Cerradura: `sops --encrypt` (o `sops -e`)

Este es el hechizo principal para cerrar tu diario secreto.

*   **¿Cómo se lanza?**
    ```bash
    # Dile a SOPS que encripte tu diario... > ...y guarde el resultado en un archivo nuevo y cerrado.
    sops --encrypt mi_diario_secreto.txt > mi_diario_cerrado.sops.txt
    ```
    (El `-e` es solo una forma más corta de escribir `--encrypt`).
*   **¿Qué hace SOPS?**
    1.  Lee tu `mi_diario_secreto.txt`.
    2.  Busca el Libro de Reglas (`.sops.yaml`) para saber qué Llave(s) Mágica(s) usar.
    3.  Crea una llave pequeñita y única solo para este diario.
    4.  Cierra el diario con la llave pequeñita.
    5.  Guarda la llave pequeñita en la caja fuerte, cerrada con la(s) Llave(s) Mágica(s) Maestra(s) del Libro de Reglas.
    6.  ¡Te da el `mi_diario_cerrado.sops.txt` que contiene el diario cerrado Y la caja fuerte con la llave pequeña dentro!
*   **¿Y si no hay Libro de Reglas?**: Si SOPS no encuentra un `.sops.yaml` con instrucciones, tendrás que decirle qué Llave Mágica usar directamente en el hechizo, así:
    ```bash
    # ¡Usa la llave PGP de Merlín!
    sops -e --pgp NUMERO_SECRETO_MERLIN mi_diario.txt > mi_diario_cerrado.sops.txt
    ```
*   **Tipos de Diarios**: SOPS es listo y sabe si tu diario es YAML, JSON, .env, etc. ¡Pero si no está seguro, puedes decírselo con `--input-type`!

### 7.2. Quitar la Cerradura: `sops --decrypt` (o `sops -d`)

¡Este es el hechizo para abrir tu diario secreto cerrado!

*   **¿Cómo se lanza?**
    ```bash
    # Para ver el secreto en la pantalla:
    sops --decrypt mi_diario_cerrado.sops.txt

    # Para guardar el secreto abierto en un archivo nuevo:
    sops --decrypt mi_diario_cerrado.sops.txt > mi_diario_abierto_otra_vez.txt
    ```
    (El `-d` es la forma corta de `--decrypt`).
*   **¿Qué hace SOPS?**
    1.  Mira el `mi_diario_cerrado.sops.txt`.
    2.  Encuentra la caja fuerte donde está guardada la llave pequeña.
    3.  Busca si tú tienes alguna de las Llaves Mágicas Maestras (PGP, age, permiso de AWS, etc.) que se usaron para cerrar esa caja fuerte.
    4.  Si tienes la llave correcta, SOPS abre la caja fuerte y saca la llave pequeña.
    5.  ¡Usa la llave pequeña para abrir el diario y te muestra el secreto!
    6.  Si no tienes ninguna llave correcta, ¡SOPS no podrá abrirlo!
*   **¡Sacar solo una palabra secreta! (`--extract`)**: A veces no quieres leer todo el diario, solo necesitas saber la contraseña del WiFi. ¡Puedes pedirle a SOPS que saque solo esa palabra!
    ```bash
    # En un diario YAML, saca solo la contraseña que está bajo "wifi" -> "password"
    sops -d --extract '["wifi"]["password"]' mi_config_cerrada.sops.yaml
    ```

### 7.3. Editar Secretos ¡Sin Abrir del Todo!: `sops <archivo>`

Este es un truco de magia muy útil. Te permite cambiar algo en tu diario secreto ¡sin tener que guardarlo abierto en tu computadora!

*   **¿Cómo se lanza?**
    ```bash
    # Simplemente dile a SOPS el nombre del diario cerrado:
    sops mi_diario_cerrado.sops.txt
    ```
*   **¿Qué hace SOPS?**
    1.  Abre el diario en secreto (en la memoria de la compu).
    2.  Lo abre en tu programa de escribir favorito (el que le dijiste a tu computadora que usara con la pista secreta `EDITOR`).
    3.  ¡Puedes escribir, borrar y cambiar cosas!
    4.  Cuando terminas de escribir y cierras el programa, ¡SOPS vuelve a cerrar el diario automáticamente con las mismas Llaves Mágicas que tenía antes!
*   **¡Cuidado!**: Asegúrate de que tu programa de escribir espere a que termines antes de devolverle el control a SOPS (programas como `nano` o `vim` lo hacen bien).

### 7.4. Otras Pistas y Opciones Mágicas

SOPS tiene más trucos bajo la manga:

*   `--config <libro_de_reglas.yaml>`: Si tu Libro de Reglas (`.sops.yaml`) no está donde SOPS busca normalmente, puedes decirle dónde está con esta opción.
*   `--set '[ruta][al][secreto] "nuevo valor"'`: ¡Un hechizo para cambiar un secreto directamente sin abrir el editor! Muy útil para robots o scripts.
    ```bash
    # Cambia la contraseña del wifi a "nueva123" sin abrir el editor
    sops --set '["wifi"]["password"] "nueva123"' mi_config_cerrada.sops.yaml
    ```
*   `--verbose` o `-v`: Si algo no funciona, usa esta opción para que SOPS te cuente más detalles de lo que está haciendo.
*   **Pistas Secretas (Variables de Entorno)**: Recuerda que SOPS busca pistas como `EDITOR`, `SOPS_PGP_FP`, `SOPS_AGE_KEY_FILE`, las de AWS, GCP, Azure, Vault, etc., para saber cómo trabajar.

¡Practica estos comandos con tus propios archivos secretos (¡primero haz una copia por si acaso!) para convertirte en un maestro de SOPS!

---

## 8. Cambiando las Cerraduras: Rotación y Actualización de Llaves (`sops updatekeys`)

Imagina que las Llaves Mágicas que usas para tus secretos son como las cerraduras de tu casa. A veces, necesitas cambiarlas:

*   Quizás perdiste una llave (¡o crees que alguien más la tiene!).
*   Quizás un amigo se muda y ya no necesita una copia de la llave.
*   Quizás llega un amigo nuevo y necesita su propia copia.
*   ¡O quizás simplemente quieres poner cerraduras más nuevas y seguras!

SOPS tiene un comando especial para esto: `sops updatekeys`. ¡Es como llamar al cerrajero mágico!

### 8.1. ¿Por Qué Cambiar las Cerraduras (Rotar Claves)?

Cambiar las cerraduras (rotar las claves) de vez en cuando es súper importante para mantener tus secretos bien seguros. Si una llave vieja se pierde o alguien que ya no debería tener acceso todavía la tiene, ¡cambiar la cerradura asegura que solo las personas correctas puedan abrir!

### 8.2. El Comando Mágico: `sops updatekeys`

Este comando es el especialista en cambiar las Llaves Mágicas Maestras que protegen un secreto SOPS.

*   **¿Cómo se lanza?**
```bash
    # Pídele a SOPS que actualice las cerraduras de este diario:
    sops updatekeys mi_diario_cerrado.sops.txt
    ```
*   **¿Qué hace SOPS?**
    1.  **Abre la cerradura vieja**: Primero, SOPS necesita abrir el `mi_diario_cerrado.sops.txt` usando las Llaves Mágicas con las que está cerrado *ahora*. ¡Así que necesitas tener acceso a una de esas llaves viejas para que funcione!
    2.  **Mira el Nuevo Libro de Reglas**: SOPS busca el Libro de Reglas (`.sops.yaml`) más cercano para ver cuáles son las *nuevas* Llaves Mágicas que debe usar.
    3.  **Pone la cerradura nueva**: Vuelve a cerrar el diario, pero esta vez usa las *nuevas* Llaves Mágicas del Libro de Reglas.
    4.  **¡Listo!**: El archivo `mi_diario_cerrado.sops.txt` ahora está protegido solo por las nuevas llaves. ¡Las viejas ya no sirven para este archivo!

### 8.3. La Forma Más Fácil: ¡Actualiza el Libro de Reglas Primero!

La manera más sencilla y ordenada de cambiar las cerraduras es:

1.  **Edita tu Libro de Reglas (`.sops.yaml`)**: Abre el archivo `.sops.yaml` y cambia la lista de llaves en la regla que aplica a tu secreto. Por ejemplo:
    *   **Añadir un amigo**: Añade el número secreto (huella PGP o clave pública age) del nuevo amigo a la lista.
    *   **Quitar un amigo**: Borra el número secreto del amigo que se fue de la lista.
    *   **Cambiar tu llave**: Reemplaza tu número secreto viejo por el nuevo.
2.  **Llama al Cerrajero Mágico (`updatekeys`)**: Ejecuta `sops updatekeys` en el archivo (o archivos) que quieres actualizar.
    ```bash
    sops updatekeys mi_diario_secreto_compartido.sops.yaml
    ```

### 8.4. ¿Qué Pasa si...? (Ejemplos)

*   **Ana se une al equipo**: Añades la llave PGP de Ana al `.sops.yaml` y ejecutas `sops updatekeys secretos_equipo.sops.yaml`. ¡Ahora Ana también puede abrirlo!
*   **Ben pierde su llave PGP**: Ben crea una llave nueva. Quitas la huella vieja de Ben del `.sops.yaml`, añades la nueva, y ejecutas `sops updatekeys secretos_equipo.sops.yaml`. ¡La llave perdida ya no sirve para esos secretos!
*   **Queremos usar solo la Llave del Castillo AWS**: Quitas todas las llaves PGP del `.sops.yaml` y dejas solo la dirección (ARN) de la Llave del Castillo AWS. Ejecutas `sops updatekeys` y ¡listo! Ahora solo se puede abrir con permiso de AWS.

### 8.5. ¡Necesitas las Llaves Viejas y las Nuevas!

Recuerda este punto importante para que `sops updatekeys` funcione:
1.  Necesitas poder **abrir el archivo AHORA** (con una de las llaves viejas).
2.  SOPS necesita poder encontrar las **nuevas** llaves públicas (o tener permiso para usar las nuevas llaves de los castillos en la nube) para poder **volver a cerrarlo** con las nuevas cerraduras.

### 8.6. Cambiar Cerraduras Directamente (Menos Común)

También puedes decirle a `sops updatekeys` exactamente qué llave añadir o quitar sin tocar el `.sops.yaml` (aunque es menos ordenado para cambios grandes):
```bash
# Añade la llave de David y quita la de Carla directamente
sops updatekeys --add-pgp NUMERO_DAVID --remove-pgp NUMERO_CARLA mi_secreto.sops.yaml
```
(Hay opciones como `--add-kms`, `--remove-age`, etc. Mira `sops updatekeys --help` para verlas todas).

**¡Importante!** El comando `sops updatekeys` cambia tu archivo secreto directamente. ¡Asegúrate de tener una copia o de usar Git por si algo sale mal!

---

## 9. Trucos de Mago y Consejos de Seguridad (Flujos de Trabajo y Mejores Prácticas)

¡Ya sabes usar los comandos básicos de SOPS! Ahora vamos a ver algunos trucos y consejos para usar SOPS como un verdadero mago de los secretos, especialmente cuando guardas tus cosas en la mochila Git o cuando necesitas que los robots ayudantes (como los de CI/CD) usen los secretos.

### 9.1. SOPS y tu Mochila Mágica (Integración con Git)

Recuerda que SOPS es genial para guardar tus diarios secretos cerrados (`*.sops.*`) dentro de tu mochila Git junto con tu código normal.

*   **¿Qué guardar en la mochila?**: ¡Sí! Guarda tus archivos secretos cerrados (los que terminan en `.sops.yaml`, `.sops.json`, etc.) y también tu Libro de Reglas (`.sops.yaml`) dentro de Git. Así, todo tu equipo tiene las mismas reglas y los mismos secretos cerrados.
*   **¡Cuidado con los diarios abiertos!**: ¡NUNCA guardes un secreto abierto (desencriptado) en tu mochila Git! Sería como dejar tu diario abierto en medio del patio. Para evitar accidentes, puedes usar un archivo especial llamado `.gitignore` (es como una lista de "cosas que la mochila debe ignorar"). Escribe en él los nombres de los archivos secretos abiertos para que Git no los guarde por error.
    ```gitignore
    # Ignora estos archivos secretos abiertos
    secrets.yaml
    database.dev.json
    *.decrypted
    ```
*   **El Guardián de la Mochila (Git Hooks)**: Para estar súper seguro, puedes poner un "guardián mágico" (un Git Hook, como `pre-commit`) en la puerta de tu mochila Git. Este guardián puede revisar automáticamente si intentas guardar un secreto sin cerrar ¡y detenerte antes de que cometas un error! Hay herramientas que te ayudan a configurar estos guardianes.

### 9.2. ¡Robots que Usan Secretos! (SOPS en CI/CD)

A veces, necesitas que tus robots ayudantes (los sistemas de Integración Continua y Entrega Continua o CI/CD, que construyen y prueban tu código automáticamente) puedan leer los secretos. Por ejemplo, para conectarse a una base de datos de prueba.

El problema es: ¿cómo le das al robot la Llave Mágica para abrir el secreto sin dejar la llave tirada donde cualquiera la vea?

Hay dos trucos principales:

*   **Truco 1: Pistas Ultra-Secretas (Variables de Entorno Seguras)**
    1.  Crea tu Llave Mágica Personal (PGP o age) o usa una Llave del Castillo (KMS, etc.) para cerrar los secretos como siempre.
    2.  Guarda la *parte secreta* de tu llave (la clave privada PGP/age) o las credenciales para hablar con el Castillo (como las claves de acceso de AWS o el token de Vault) en un lugar súper secreto que solo los robots puedan ver. ¡Todas las herramientas de CI/CD (GitHub Actions, GitLab CI, Jenkins) tienen una caja fuerte especial para esto (Secrets o Variables Protegidas)!
    3.  Cuando el robot necesite abrir el secreto, le das una "pista secreta" (una variable de entorno segura) que contenga la llave privada o las credenciales. Por ejemplo, le das la pista `SOPS_AGE_KEY=...` o `AWS_ACCESS_KEY_ID=...`.
    4.  ¡SOPS usará esa pista secreta para encontrar la llave y abrir el secreto sin que la llave esté escrita en el código del robot!
*   **Truco 2: ¡Permiso Mágico Directo! (Roles IAM y Similares)**
    1.  Este truco funciona si usas las Llaves de los Castillos en la Nube (AWS KMS, GCP KMS, Azure Key Vault).
    2.  En lugar de darle al robot una llave secreta, ¡le das un **permiso mágico** directamente en el castillo (un Rol IAM en AWS, una Identidad de Carga de Trabajo en GCP, una Identidad Administrada en Azure)!
    3.  Este permiso le dice al castillo: "¡Oye, este robot es de confianza! Si te pide abrir la caja fuerte `DIRECCION_CAJA_FUERTE_1`, ¡déjale!".
    4.  Cuando el robot ejecuta `sops -d`, SOPS habla con el castillo, el castillo ve que el robot tiene el permiso mágico, ¡y le ayuda a abrir el secreto!
    5.  ¡Esta es la forma **más segura** de usar SOPS con robots en la nube, porque no necesitas guardar ninguna llave secreta en la configuración del robot!

### 9.3. ¡Protege tus Llaves Mágicas Maestras!

Recuerda: ¡La seguridad de tus secretos depende de lo bien que guardes tus Llaves Mágicas Maestras!

*   **Llaves Personales (PGP/age)**:
    *   Si usas PGP, ¡ponle una **contraseña súper fuerte** a tu llave privada! Así, aunque alguien copiara el archivo de tu llave, no podría usarla sin la contraseña.
    *   Guarda los archivos de tus claves privadas (`.asc`, `.key`, los de age) en un lugar muy seguro de tu computadora, donde solo tú tengas acceso.
    *   Para máxima seguridad, ¡puedes guardar tu llave PGP en una varita mágica física (como una YubiKey)! Es como tener una caja fuerte real para tu llave.
*   **Llaves de los Castillos (KMS/GCP/Azure/Vault)**:
    *   Usa el **"Principio del Menor Poder Mágico"**: No le des a la gente ni a los robots más permisos de los que necesitan. Si un robot solo necesita *abrir* secretos, ¡dale permiso solo para abrir (`kms:Decrypt`), no para cerrar (`kms:Encrypt`)!
    *   Si usas claves de acceso (como en AWS), ¡cámbialas de vez en cuando (rótalas)!
*   **¡Haz Copias de Seguridad!**: ¿Qué pasaría si pierdes tu única Llave Mágica? ¡No podrías abrir tus secretos! Haz copias de seguridad de tus claves privadas PGP/age (¡y anota la contraseña de PGP en un lugar seguro!) y guárdalas en un lugar súper seguro (¡quizás en una caja fuerte diferente o en una mochila mágica de respaldo!).

### 9.4. ¿Quién Ha Estado Usando las Llaves? (Auditoría)

A veces quieres saber cuándo se cambió un secreto o quién lo abrió.

*   **SOPS Guarda Pistas**: Dentro de cada archivo SOPS, hay pequeñas notas (`lastmodified`, `mac`) que cambian cada vez que editas el archivo.
*   **¡Los Castillos Tienen Ojos!**: Si usas las Llaves de los Castillos (KMS, GCP, Azure, Vault), ¡ellos suelen tener un registro (logs de auditoría) de quién les pidió usar una llave y cuándo! Esto es muy útil para saber quién ha estado accediendo a los secretos.

### 9.5. ¡Organiza tus Secretos!

Si tienes muchos secretos, no los guardes todos en un solo diario gigante. ¡Se volvería un lío!

*   **Separa los Diarios**: Crea diferentes archivos SOPS para diferentes cosas. Por ejemplo:
    *   Un diario para los secretos de la base de datos: `database.sops.yaml`
    *   Un diario para las llaves de servicios externos: `api-keys.sops.env`
    *   Diarios diferentes para desarrollo y producción: `config.dev.sops.yaml`, `config.prod.sops.yaml`.
*   **Usa Carpetas**: Organiza tus diarios secretos en carpetas con nombres claros.
*   **Reglas Específicas**: Usa la magia del `path_regex` en tu Libro de Reglas (`.sops.yaml`) para aplicar diferentes Llaves Mágicas o reglas a diferentes carpetas o tipos de diarios.

¡Con estos trucos y consejos, puedes usar SOPS de forma segura y organizada, tanto solo como en equipo!

---

## 10. Resolución de Problemas Comunes

A veces, hasta la magia más poderosa puede encontrar un pequeño tropiezo. ¡No te preocupes! Aquí tienes una guía para resolver los problemas más comunes que puedes encontrar con SOPS.

*   **Problema: "¡No puedo abrir mi secreto! SOPS dice `no matching MAC` (MAC no coincide) o `failed to decrypt DEK` (falló al desencriptar la DEK)."**
    *   **¿Qué pasa?**: Este es un mensaje general que significa que SOPS no pudo abrir la caja fuerte de la llave pequeña (DEK) o que el contenido del diario parece haber cambiado sin que SOPS se diera cuenta.
    *   **Causas y Soluciones Mágicas**:
        1.  **¿Se modificó el diario sin usar `sops`?**: Si abriste el archivo `.sops.yaml` con un editor normal y lo guardaste, ¡podrías haber roto la cerradura mágica!
            *   **Solución**: Intenta recuperarlo de una copia de seguridad (Git es tu amigo aquí, si guardaste versiones anteriores). Siempre edita archivos SOPS con el comando `sops <nombre_archivo.sops.yaml>`.
        2.  **¿Tienes la Llave Mágica correcta?**:
            *   **PGP**: ¿Está tu llave privada PGP cargada en tu llavero GPG? ¿Es la llave correcta (la huella digital coincide con la que está en el archivo SOPS o en `.sops.yaml`)? ¿Necesitas introducir tu contraseña PGP?
            *   **age**: ¿El archivo de tu clave privada `age` está donde SOPS espera encontrarlo (quizás necesitas la pista secreta `SOPS_AGE_KEY_FILE`)? ¿Es la clave privada que corresponde a una de las claves públicas usadas para cerrar el secreto?
            *   **KMS/GCP/Azure/Vault**: ¿Tienes las credenciales correctas configuradas en tu computadora (pistas secretas de AWS, GCP, Azure, Vault)? ¿Tienes permiso para usar la Llave del Castillo específica que cierra este secreto?
        3.  **¿Está corrupto el archivo?**: Es raro, pero a veces los archivos se dañan.
            *   **Solución**: De nuevo, ¡copias de seguridad!

*   **Problema: "SOPS dice que no encuentra mi llave PGP (`No PGP key matching fingerprint ... found`)"**
    *   **¿Qué pasa?**: SOPS sabe qué llave PGP buscar (por su huella digital), ¡pero no la encuentra en tu llavero GPG!
    *   **Causas y Soluciones Mágicas**:
        1.  **¿Está `gpg` instalado y funcionando?**: Prueba a escribir `gpg --version` en tu terminal.
        2.  **¿Dónde están tus llaves GPG?**: SOPS busca en la carpeta normal (`~/.gnupg`). Si tus llaves están en otro sitio, dile a SOPS dónde buscar con la pista secreta `GNUPGHOME=/ruta/a/tus/llaves`.
        3.  **¿Está la llave en tu llavero?**: Usa `gpg --list-secret-keys` para ver las huellas de las llaves privadas que tienes. ¿Coincide alguna con la que busca SOPS? Quizás necesitas importar la llave privada a tu llavero.
        4.  **¿Huella incorrecta en `.sops.yaml` o en el archivo?**: Verifica que la huella digital (fingerprint) en tu Libro de Reglas o la que SOPS te dice que busca sea exactamente la misma que la de tu llave.

*   **Problema: "SOPS no encuentra mi llave `age` (`No age key found for recipient ...`)"**
    *   **¿Qué pasa?**: SOPS busca una clave privada `age` que corresponda a una de las claves públicas usadas para cerrar el secreto, ¡pero no la encuentra!
    *   **Causas y Soluciones Mágicas**:
        1.  **¿Dónde está tu archivo de clave privada `age`?**: SOPS busca en lugares estándar (como `~/.config/sops/age/keys.txt` o `~/.ssh/id_age`) o donde le digas con la pista secreta `SOPS_AGE_KEY_FILE=/ruta/a/tu/clave_privada.txt`. Asegúrate de que el archivo esté ahí y SOPS pueda leerlo.
        2.  **¿Es la clave privada correcta?**: La clave privada debe ser la pareja de una de las claves públicas (recipientes) que se usaron para cerrar el secreto.

*   **Problema: "¡No puedo conectarme al Castillo en la Nube! (Errores con AWS KMS, GCP KMS, Azure Key Vault, o HashiCorp Vault)"**
    *   **¿Qué pasa?**: SOPS no puede hablar con el servicio de la nube o con Vault para usar la Llave Maestra.
    *   **Causas y Soluciones Mágicas (varían según el castillo)**:
        *   **AWS KMS**:
            *   ¿Pistas secretas de AWS (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`, `AWS_REGION`) bien configuradas?
            *   ¿Permisos IAM correctos para usar la llave KMS (acciones como `kms:Decrypt` para abrir, `kms:Encrypt` o `kms:GenerateDataKey` para cerrar)?
            *   ¿El ARN de la llave KMS en `.sops.yaml` es correcto y está en la región correcta?
        *   **GCP KMS**:
            *   ¿Pista secreta `GOOGLE_APPLICATION_CREDENTIALS` apuntando a un archivo de credenciales de cuenta de servicio válido?
            *   ¿La cuenta de servicio tiene los roles/permisos correctos en GCP para usar la llave KMS (ej. "Cloud KMS CryptoKey Decrypter/Encrypter")?
        *   **Azure Key Vault**:
            *   ¿Pistas secretas de Azure (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` o usando Identidad Administrada) bien configuradas?
            *   ¿El Principal de Servicio (o Identidad Administrada) tiene los permisos correctos (ej. "get" y "unwrapKey" para claves) en la Política de Acceso del Key Vault?
            *   ¿La URL de la llave en `.sops.yaml` es correcta?
        *   **HashiCorp Vault**:
            *   ¿Pistas secretas `VAULT_ADDR` (dirección del servidor Vault) y `VAULT_TOKEN` (token de acceso) bien configuradas?
            *   ¿El token de Vault tiene permiso para usar la ruta `transit` especificada en `.sops.yaml`?

*   **Problema: "Abro el archivo con `sops <archivo>`, edito, guardo, ¡pero los cambios no se quedan!"**
    *   **¿Qué pasa?**: SOPS usa tu editor de texto configurado con la pista secreta `EDITOR`. Si ese editor no "bloquea" (espera a que lo cierres) antes de devolver el control a SOPS, SOPS podría pensar que terminaste antes de tiempo y no guardar los cambios.
    *   **Solución Mágica**: Configura tu pista `EDITOR` para que use un editor de terminal que sí espere, como `nano`, `vim`, `emacs -nw`, etc. Ejemplo: `export EDITOR=nano`.

*   **Problema: "SOPS dice `sops metadata missing` (faltan metadatos de SOPS) o algo parecido."**
    *   **¿Qué pasa?**: Estás intentando usar un comando de SOPS (como `sops -d`) en un archivo que no parece ser un archivo cerrado por SOPS, o que está muy dañado.
    *   **Solución Mágica**: Asegúrate de que estás apuntando al archivo correcto (el que termina en `.sops.yaml`, `.sops.json`, etc., y que fue cerrado previamente con SOPS). Si es un archivo nuevo que quieres cerrar por primera vez, ¡necesitas usar `sops -e` (o `sops --encrypt`)!

*   **Problema: "SOPS se queja del `shamir_threshold` (umbral de Shamir)."**
    *   **¿Qué pasa?**: Si usas `key_groups` con un `shamir_threshold` (por ejemplo, necesitas 2 de 3 llaves para abrir un cofre), SOPS te dirá si no encuentra suficientes llaves disponibles para alcanzar ese número mágico.
    *   **Solución Mágica**: Verifica cuántas de las Llaves Mágicas listadas en ese `key_group` están realmente disponibles y accesibles para ti (¿tienes las claves privadas PGP/age correctas cargadas? ¿tienes los permisos de nube necesarios?). Asegúrate de que el número de llaves disponibles sea igual o mayor que el `shamir_threshold`.

¡Con un poco de paciencia y estos consejos, deberías poder resolver la mayoría de los misterios de SOPS! Si te atascas mucho, la opción `--verbose` (o `-v`) con los comandos de SOPS te puede dar más pistas sobre lo que está pasando.

---
<!-- Siguiente sección: ## 11. Apéndice: Formatos de Archivo Detallados (Opcional) -->
## 11. Apéndice: Formatos de Archivo Detallados (Opcional)

## 12. Apéndice: Uso de SOPS con `git-tokens.py` en este Proyecto

<!-- Sección específica del proyecto -->

## Apéndice A: Formatos de Archivo Detallados (Opcional)

Esta sección es para los magos más curiosos que quieren ver cómo está construido un diario secreto cerrado por SOPS por dentro. No necesitas saber esto para usar SOPS, ¡pero puede ser interesante!

Cuando SOPS cierra un archivo (por ejemplo, un `mi_secreto.yaml`), el archivo resultante (`mi_secreto.sops.yaml`) sigue siendo un archivo YAML válido. ¡Lo mismo pasa con JSON, .env, etc.! SOPS es listo y mantiene la estructura original de tu archivo, pero con dos cambios principales:

1.  **Valores Secretos Encerrados**: Las palabras secretas que le dijiste a SOPS que cerrara (usando `encrypted_regex` en tu Libro de Reglas o porque SOPS las detectó) se reemplazan por un texto especial que empieza con `ENC[...]`. Este texto es el secreto cerrado con la llave pequeña (DEK).
2.  **La Caja Fuerte de SOPS (`sops`)**: SOPS añade una nueva sección especial al final de tu archivo (o al principio, dependiendo del formato). Esta sección se llama `sops` y es como la caja fuerte mágica donde se guarda toda la información para abrir el diario.

### A.1. Dentro de la Caja Fuerte (`sops`)

La sección `sops` contiene varias piezas importantes:

*   `dek`: Esta es la **Llave de Encriptación de Datos (Data Encryption Key)**. Es la llave pequeña y única que SOPS creó específicamente para cerrar *este* diario. ¡Pero no te preocupes! La DEK que ves aquí está, a su vez, **cerrada (encriptada)** con una o varias de tus Llaves Mágicas Maestras (PGP, age, KMS, etc.).
*   `mac`: Es el **Código de Autenticación de Mensaje (Message Authentication Code)**. Es como un sello mágico que SOPS usa para asegurarse de que nadie ha cambiado el diario (ni la sección `sops`) sin permiso desde la última vez que se cerró. Si este sello no coincide, SOPS no abrirá el diario (¡y te dará un error de MAC!).
*   `version`: La versión de la herramienta SOPS que se usó para cerrar este archivo por última vez.
*   `lastmodified`: Una nota que dice cuándo se cerró este archivo por última vez (fecha y hora).
*   **Proveedores de Llaves (PGP, age, KMS, etc.)**: ¡Esta es la parte más importante de la caja fuerte! Por cada tipo de Llave Mágica Maestra que usaste para cerrar el secreto (según tu Libro de Reglas), habrá una sección aquí. Por ejemplo:
    *   `pgp`: Una lista. Cada elemento representa una llave PGP que puede abrir este secreto. Dentro de cada elemento encontrarás:
        *   `fp`: La huella digital (fingerprint) de la llave PGP.
        *   `created_at`: Cuándo se añadió esta llave PGP al archivo SOPS.
        *   `enc`: ¡La DEK cerrada (encriptada) específicamente con esta llave PGP pública! Solo la persona con la llave privada PGP correspondiente podrá abrir esta `enc` para obtener la DEK.
    *   `age`: Similar a `pgp`, una lista. Cada elemento tiene:
        *   `recipient`: La clave pública `age`.
        *   `created_at`: Cuándo se añadió.
        *   `enc`: La DEK cerrada con esta clave pública `age`.
    *   `kms`, `gcp_kms`, `azure_keyvault`, `hc_vault`: Listas para cada tipo de Llave de Castillo. Cada elemento describe una llave específica del castillo que puede abrir el secreto, e incluye:
        *   `arn` (para AWS), `resource_id` (para GCP), `uri` (para Azure), `transit_path` y `key_name` (para Vault): La dirección mágica de la llave en el castillo.
        *   `created_at`: Cuándo se añadió.
        *   `enc`: ¡La DEK cerrada (encriptada) usando la magia de esta Llave del Castillo! SOPS le pide al castillo que la abra.
        *   A veces hay más información, como `aws_profile`, `role`, `encryption_context` (para AWS) para dar más detalles sobre cómo usar la llave del castillo.
*   `key_groups`: Si usaste la magia de los Grupos de Claves y el Umbral de Shamir, esta sección aparecerá. Será una lista, donde cada elemento es un "cofre" (`key_group`).
    *   Dentro de cada cofre, verás las mismas secciones `pgp`, `age`, `kms`, etc., que describimos antes, detallando las llaves que están *dentro* de ese cofre.
    *   También verás `shamir_threshold`: El número mágico que dice cuántas de las llaves de *este cofre* se necesitan para abrirlo y obtener la DEK.

### A.2. ¿Cómo se ven las Palabras Secretas Encerradas?

En tu archivo YAML, JSON, etc., donde antes tenías `mi_contraseña_secreta`, ahora verás algo como:

`ENC[AES256_GCM,data:ABCDE...,iv:FGHIJ...,tag:KLMNO...]`

*   `ENC[...]`: Indica que esto es un valor cerrado por SOPS.
*   `AES256_GCM`: El tipo de magia (algoritmo de cifrado) que SOPS usó para cerrar la palabra con la DEK.
*   `data`: La palabra secreta, pero cerrada (cifrada).
*   `iv`: Un "vector de inicialización", un número mágico que ayuda a que el cierre sea único cada vez.
*   `tag`: Otro sello mágico para asegurar que la palabra cerrada no se haya modificado.

¡Y eso es todo! Es como ver los engranajes de un reloj mágico. No necesitas tocarlos, ¡pero es genial saber que están ahí trabajando para mantener tus secretos a salvo!

---
<!-- Siguiente sección: ## 12. Apéndice: Uso de SOPS con git-tokens.py en este Proyecto -->

## Apéndice B: Gestión de Archivos de Tokens de Servidores Git con SOPS y `git-tokens.py`

Este apéndice detalla cómo la herramienta `git-tokens.py` de este proyecto utiliza SOPS para gestionar de forma segura los tokens de acceso a servidores Git.

### B.1. Propósito de los Archivos de Token

La utilidad `git-tokens.py` está diseñada para simplificar y asegurar la gestión de credenciales (tokens de acceso personal, contraseñas de aplicación, etc.) necesarias para interactuar con diversos servidores Git como GitHub, GitLab, Gitea, entre otros. Para lograr esto, `git-tokens.py` almacena cada token en un archivo individual, debidamente encriptado mediante SOPS.

### B.2. Formato del Nombre del Archivo de Token

Los archivos que almacenan los tokens siguen una convención de nomenclatura estricta para su correcta identificación y procesamiento por `git-tokens.py`:

`token_%s.git.sops.yaml`

Donde:
*   `token_`: Es un prefijo fijo que identifica el propósito del archivo.
*   `%s`: Representa un **identificador único** para el servidor Git o la cuenta específica asociada al token. Por ejemplo, `github_com_usuario1`, `gitea_trabajo`, `gitlab_proyecto_x`. Este identificador es crucial para que `git-tokens.py` pueda localizar y gestionar el token correcto.
*   `.git`: Un segmento fijo que indica explícitamente que el token es para un servidor Git.
*   `.sops.yaml`: Es la extensión estándar que denota que el archivo es un documento YAML encriptado utilizando SOPS.

### B.3. Ubicación de los Archivos de Token

La herramienta `git-tokens.py` determina la ubicación para almacenar y leer estos archivos de token de la siguiente manera:

1.  Intenta leer una ruta personalizada desde el archivo `~/bin/sops/devspath.def`. Si este archivo existe y contiene una ruta válida, esa será la ubicación utilizada.
2.  Si el archivo `devspath.def` no existe, no es accesible, o no contiene una ruta válida, `git-tokens.py` recurre a una **ubicación por defecto**: `~/.sops/`. Es en este directorio donde se guardarán y buscarán los archivos `token_*.git.sops.yaml`.

### B.4. Estructura Interna del Archivo de Token (antes de la encriptación SOPS)

Antes de que SOPS aplique su magia de encriptación, cada archivo de token es un simple documento YAML. La estructura de este YAML se basa en la plantilla definida en `config/token_git_sops.def` dentro de este proyecto. Contiene dos claves principales:

*   `git_server`: (String) La URL base canónica y completa del servidor Git al que pertenece el token. Este campo sirve como un identificador informativo y puede ser usado para validaciones o para conexión a servidores git propios.
    *   Ejemplo: `https://github.com`, `https://gitlab.com`, `https://gitea.midominio.privado.com`
*   `git_token`: (String) El token de acceso personal (PAT), contraseña de aplicación, u otra credencial secreta utilizada para la autenticación con el servidor Git. **Importante**: El valor de este token se almacena **codificado en Base64** dentro del archivo YAML, *antes* de que SOPS encripte todo el archivo. SOPS, por lo tanto, encriptará la cadena Base64 del token.

**Ejemplo de contenido para un archivo YAML temporal (ej. `token_github_com.git.yaml`) antes de la encriptación SOPS:**

```yaml
# Contenido de token_github_com.git.yaml (antes de encriptar)
git_server: "https://github.com"
git_token: "Z2hwX0FiY0RlZmdoaUpLbE1uT3BxUnN0VXZXeXpaMTIzNDU2Nzg5MA==" # Ejemplo: "ghp_AbcDefghiJKlMnOpqRstUvWXyz1234567890" codificado en Base64
```

### B.5. Encriptación con SOPS

El script `git-tokens.py` orquesta el proceso de encriptación. Cuando se añade un nuevo token:

1.  `git-tokens.py` toma el token original proporcionado por el usuario.
2.  Codifica este token en Base64.
3.  Construye el contenido YAML (como se muestra en el ejemplo anterior) con la URL del servidor y el token ya codificado en Base64.
4.  Invoca a SOPS (`sops -e`) para encriptar este archivo YAML temporal.
5.  La encriptación se realiza conforme a las reglas definidas en un archivo `.sops.yaml` presente en el sistema (cuya plantilla inicial puede derivarse de `config/sops_rules.def`). Esta regla especifica, crucialmente, el uso de una clave PGP (identificada mediante la huella `${git_fingerprint}`) para proteger estos archivos de token.
6.  SOPS encripta los valores dentro del YAML (especialmente la cadena Base64 del `git_token`) y añade su propia sección de metadatos `sops` (ver Apéndice A para detalles sobre esta sección), guardando el resultado final en la ubicación determinada (ver B.3) con el nombre formateado `token_%s.git.sops.yaml`.

### B.6. Administración Integral por `git-tokens.py`

La herramienta `git-tokens.py` actúa como la interfaz principal y única para la gestión completa del ciclo de vida de estos archivos de token encriptados, abstrayendo la complejidad de SOPS y la codificación Base64 del usuario:

*   **Creación (`add` command)**: `git-tokens.py` solicita interactivamente al usuario el identificador para el token (que formará parte del nombre del archivo), la URL del servidor Git y el token secreto. Internamente, codifica el token a Base64, genera el archivo YAML temporal, y luego utiliza `sops --encrypt` para crear el archivo `token_%s.git.sops.yaml` encriptado en la ubicación correcta.
*   **Eliminación (`remove` command)**: `git-tokens.py` elimina de forma segura el archivo `token_*.git.sops.yaml` especificado del sistema de archivos, revocando efectivamente el acceso al token a través de esta herramienta.

### B.7. Beneficios de esta Arquitectura

*   **Seguridad en Reposo Robusta**: Los tokens de Git, que son credenciales altamente sensibles, están protegidos en el disco mediante la encriptación PGP fuerte proporcionada por SOPS. La codificación Base64 previa añade una capa de ofuscación, aunque la seguridad principal recae en SOPS.
*   **Gestión Centralizada y Simplificada**: `git-tokens.py` ofrece una interfaz de línea de comandos cohesiva y fácil de usar, ocultando los detalles de la interacción con SOPS y el manejo de archivos.
*   **Acceso Controlado por PGP**: El acceso a los tokens originales está intrínsecamente ligado a la posesión de la clave privada PGP correcta. Sin ella, los archivos encriptados por SOPS son indescifrables.
*   **Portabilidad Condicionada**: Los archivos de token encriptados pueden ser transferidos a otras máquinas, pero solo serán utilizables si la clave PGP privada correspondiente también está disponible y configurada en el nuevo entorno.

Este sistema proporciona un equilibrio entre seguridad robusta para credenciales sensibles y una gestión práctica a través de la herramienta `git-tokens.py`.

---
