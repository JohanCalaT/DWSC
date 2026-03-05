# Proyecto Universidad: RESTful API .NET 10 + PostgreSQL

Este proyecto es una actividad académica sobre servicios web RESTful. Implementa un sistema CRUD para gestionar información de estudiantes utilizando las tecnologías más recientes.

## 🚀 Tecnologías
- **.NET 10** (ASP.NET Core Web API)
- **PostgreSQL** (Docker Desktop)
- **Entity Framework Core** (Npgsql)
- **Swagger/OpenAPI** (Documentación Interactiva)

---

## 📚 Respuestas Teóricas

1. **¿Qué es un servicio web y cuáles son sus características?**
   Es un sistema de software diseñado para soportar la interacción interoperable máquina a máquina sobre una red. Sus características incluyen: interoperabilidad, uso de protocolos estándar (HTTP), y descripción de servicios.

2. **¿Diferencia entre SOAP y REST?**
   **SOAP** es un protocolo rígido basado en XML que usa WSDL para definirse. **REST** es un estilo arquitectónico más flexible que usa diversos formatos (principalmente JSON), es más ligero y utiliza directamente los verbos HTTP.

3. **¿Qué son los métodos HTTP y para qué sirve cada uno?**
   - **GET**: Recuperar información.
   - **POST**: Crear un nuevo recurso.
   - **PUT**: Actualizar un recurso existente de forma completa.
   - **DELETE**: Eliminar un recurso.

4. **¿Qué es JSON y por qué se usa en REST?**
   JavaScript Object Notation. Se usa por ser ligero, fácil de leer por humanos y máquinas, y ser el estándar de facto para la comunicación en la web moderna.

5. **¿Qué es ASP.NET Core Web API vs Jersey?**
   ASP.NET Core es el framework de Microsoft para construir APIs en C#. Jersey es la implementación de referencia de JAX-RS para Java. Ambos sirven el mismo propósito: simplificar la creación de servicios REST.

6. **¿Qué es Entity Framework Core?**
   Es un mapeador objeto-relacional (ORM) que permite a los desarrolladores trabajar con bases de datos usando objetos de .NET, eliminando la necesidad de escribir la mayor parte del código SQL.

7. **¿Qué es una API RESTful y sus principios?**
   Es una API que sigue los principios de REST: arquitectura cliente-servidor, sin estado (stateless), cacheable, sistema de capas e interfaz uniforme.

8. **¿Qué es Swagger/OpenAPI?**
   Es un conjunto de herramientas para documentar, visualizar y probar APIs REST de forma interactiva directamente desde el navegador.

9. **¿Qué son los códigos de estado HTTP?**
   Son respuestas numéricas del servidor (ej: 200, 404, 500) que indican el resultado de una solicitud. Son vitales en REST para que el cliente sepa exactamente qué ocurrió sin analizar el cuerpo de la respuesta.

10. **¿Por qué Docker para la BD?**
    Permite encapsular la base de datos con toda su configuración en un contenedor, garantizando que funcione igual en cualquier máquina sin necesidad de instalaciones manuales.

---

## 🛠️ Instalación y Ejecución

### Requisitos Previos
- Docker Desktop
- .NET 10 SDK

### Pasos
1. **Clonar el repositorio.**
2. **Levantar la base de datos:**
   ```bash
   docker-compose up -d
   ```
3. **Ejecutar la API:**
   ```bash
   cd UniversidadAPI
   dotnet run
   ```
4. **Acceder a Swagger:**
   Vaya a `http://localhost:5000/swagger` (o el puerto indicado en la consola) para probar los endpoints.

---

## 🧪 Guía de Pruebas (cURL)

| Acción | Comando | Código Esperado |
|--------|---------|-----------------|
| GET Todos | `curl -X GET http://localhost:5000/api/estudiantes` | 200 OK |
| GET ID 1 | `curl -X GET http://localhost:5000/api/estudiantes/1` | 200 OK |
| POST Crear | `curl -X POST http://localhost:5000/api/estudiantes -H "Content-Type: application/json" -d '{"nombre":"Luis","apellido":"Paz","email":"luis.paz@mail.com","carrera":"Arte","semestre":1}'` | 201 Created |
| PUT Act. | `curl -X PUT http://localhost:5000/api/estudiantes/1 -H "Content-Type: application/json" -d '{"id":1,"nombre":"Juan Modificado",...}'` | 204 No Content |
| DELETE | `curl -X DELETE http://localhost:5000/api/estudiantes/1` | 204 No Content |
| Error 404 | `curl -X GET http://localhost:5000/api/estudiantes/999` | 404 Not Found |
