```
src/
├── core/                      # Funciones y utilidades comunes
│   ├── errorhandlers.py      
│   ├── logger.py              
│   └── responses.py           # Respuestas para la API
├── models/                    # Definiciones de modelos (base de datos)
│   ├── base/                  # Funciones base para los modelos
│   │   └── mixins.py          
│   ├── Models.py
├── repositories/              # Repositorios para acceso a la base de datos
│   ├── base/                  # Funciones base para los repositorios
│   │   └── mixins.py          
│   ├── ModelsRepositories.py            
├── resources/                 # Recursos (endpoints de la API)
│   ├── base/                  # Recursos base (heredados por otros recursos)
│   │   └── custom_resource.py 
│   └── ModulesResources.py    
├── schemas/                   # Definiciones de esquemas
│   ├── base_schema.py         
│   └── ModulesResources.py      
├── config.py                   # Archivo de configuración general
├── extensions.py              # Extensiones de Flask (por ejemplo, SQLAlchemy, Marshmallow)
├── routes.py                  # Definición de las rutas de la aplicación
└── setup.py                   # Script de configuración del proyecto
```
