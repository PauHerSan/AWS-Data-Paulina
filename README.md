**Pasos para la instalación de python:**  
***Descarga el instalador:***

1. Abre tu navegador y ve al sitio web oficial de Python: [https://www.python.org/downloads/](https://www.python.org/downloads/).    
     
2. Haz clic en el botón para descargar la última versión de Python para Windows. 

***Ejecuta el instalador:*** 

3. Localiza el archivo .exe descargado y haz doble clic para ejecutarlo. 

   En la ventana del instalador, es muy importante que marques la casilla "Add python.exe to PATH". Esto permitirá ejecutar Python desde cualquier ubicación en la línea de comandos. 

4. Haz clic en "Install Now" o "Instalar" para iniciar la instalación. 

***Verifica la instalación:***

5. Una vez que la instalación termine, abre la ventana del Símbolo del sistema (CMD). Puedes hacerlo buscando "cmd" en el menú de inicio de Windows.   
     
6. Escribe el comando python \--version o python \-V y presiona Enter. 

7. Si la instalación fue correcta, el CMD mostrará la versión de Python que has instalado, indicando que Python está configurado correctamente en tu sistema.

**Pasos para la instalación de Docker:**

1. *Descarga Docker Desktop:* Ve al sitio oficial de Docker Docs ([https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)) y descarga el instalador compatible con tu versión de Windows.  
     
2. *Ejecuta el instalador:* Haz doble clic en el archivo descargado para iniciar el proceso.  
     
3. *Configura la instalación:* Durante la instalación, asegúrate de seleccionar la opción para habilitar WSL 2 (Subsistema de Windows para Linux) como backend.  
     
4. *Completa la instalación:* Haz clic en "Instalar" y espera a que termine el proceso. Es posible que necesites reiniciar tu sistema operativo.   
   

**Verifica la instalación**

5. *Inicia Docker Desktop*: Abre Docker Desktop desde el menú de inicio de Windows.  
     
6. *Configura WSL 2:* Si es la primera vez que lo ejecutas, se te pedirá configurar WSL 2 como el backend predeterminado, acepta esta configuración.  
     
7. *Ejecuta una prueba:* Abre una terminal (como PowerShell o Símbolo del sistema) y escribe el siguiente comando para verificar que Docker está funcionando correctamente:

   bash

   docker run hello-world

   Este comando descargará una imagen de prueba y ejecutará un contenedor que imprimirá un mensaje de bienvenida.

**Pasos para crear y activar un entorno virtual:**

1. Abre la terminal o símbolo del sistema en la ubicación de tu proyecto.  
     
2. Crea el entorno virtual con el módulo venv:

   bash

   python \-m venv \<nombre\_del\_entorno\>

   Reemplaza \<nombre\_del\_entorno\> con el nombre que desees, por ejemplo, .venv o mi\_entorno. Esto creará una carpeta que contiene el entorno aislado.

3. Activa el entorno virtual:

   En Windows:

   

   bash

   .\<nombre\_del\_entorno\>\\Scripts\\activate

 


4. Después de ejecutar el comando, verás el nombre de tu entorno entre paréntesis al inicio de la línea de comandos (por ejemplo, (.venv) C:\\ruta\\a\\tu\\proyecto\>), indicando que está activo. 

**Ventajas de los entornos virtuales**

* *Aislamiento*: Permite instalar diferentes versiones de librerías para distintos proyectos sin que interfieran entre sí.  
    
* *Control de dependencias:* Facilita la gestión de paquetes específicos para cada proyecto, evitando conflictos entre ellos.