# AjoloEats: Demostración de Arquitectura Orientada a Eventos con AWS

Una demostración práctica de arquitecturas orientadas a eventos utilizando servicios de AWS. Este proyecto muestra cómo construir aplicaciones escalables y desacopladas usando AWS Lambda, Amazon EventBridge y Amazon SES a través de un sistema simple de notificaciones de entrega de comida.

## 🎯 Descripción General del Proyecto

AjoloEats demuestra patrones orientados a eventos a través de un flujo simple pero completo de notificaciones de entrega de comida. Cuando los usuarios envían pedidos a través de un formulario, el sistema procesa estos eventos y desencadena varias acciones posteriores.

## 🏗️ Componentes de la Arquitectura

- Formulario frontend para envío de pedidos
- Funciones AWS Lambda para procesamiento de eventos
- Amazon EventBridge para el enrutamiento de eventos
- Amazon SES para notificaciones por correo electrónico
- OpenTofu para infraestructura como código

## 🔄 Flujo de Eventos

1. Usuario envía pedido a través del formulario web
2. Función Lambda procesa el envío del formulario
3. Los eventos se publican en EventBridge
4. Diferentes funciones Lambda se suscriben a patrones específicos de eventos
5. Las notificaciones por correo electrónico se envían a través de SES basadas en eventos

## 💡 Objetivos de Aprendizaje

Esta demostración ayuda a los desarrolladores a entender:
- Principios de arquitectura orientada a eventos
- Integración de servicios serverless de AWS
- Enrutamiento y filtrado de eventos
- Patrones de procesamiento asíncrono
- Prácticas de Infraestructura como Código

## 🚀 Comenzando

Consulta `SETUP.md` para instrucciones detalladas de despliegue y prerrequisitos.

## 📚 Documentación

La documentación detallada, incluyendo diagramas de arquitectura y ejemplos de patrones de eventos, se encuentra en el directorio `docs/`.

## 🔑 Prerrequisitos

- Cuenta de AWS
- AWS CLI [configurado](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
- Python 3.11 o superior

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo `LICENSE` para más detalles.