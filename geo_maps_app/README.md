# 📍 GeoMaps — App de Geolocalización con Google Maps

Aplicación Flutter de geolocalización en tiempo real con Google Maps, desarrollada como proyecto educativo completo.

---

## 🗂️ Estructura del proyecto

```
geo_maps_app/
├── lib/
│   ├── main.dart                    # Entry point
│   ├── app.dart                     # Widget raíz + tema
│   ├── config/
│   │   └── app_config.dart          # Constantes y configuración de API
│   ├── models/
│   │   └── location_model.dart      # Modelos de datos (LocationModel, MapMarkerModel)
│   ├── services/
│   │   ├── location_service.dart    # Servicio GPS (geolocator)
│   │   └── geocoding_service.dart   # Geocodificación inversa
│   ├── providers/
│   │   └── location_provider.dart   # Gestión de estado con Provider
│   ├── screens/
│   │   ├── splash_screen.dart       # Pantalla de bienvenida
│   │   ├── home_screen.dart         # Pantalla principal
│   │   └── location_history_screen.dart  # Historial de ubicaciones
│   ├── widgets/
│   │   ├── map_widget.dart          # Widget del mapa de Google
│   │   ├── location_info_card.dart  # Panel inferior con datos GPS
│   │   ├── map_controls_widget.dart # Botones flotantes de control
│   │   ├── map_type_selector.dart   # Selector de tipo de mapa
│   │   └── permission_error_widget.dart  # UI de errores de permisos
│   ├── utils/
│   │   ├── map_utils.dart           # Cálculos geográficos (haversine, DMS, etc.)
│   │   ├── permission_utils.dart    # Diálogos de permisos
│   │   └── app_strings.dart         # Cadenas de texto centralizadas
│   └── theme/
│       └── app_theme.dart           # Design system (colores, tipografía, tema)
├── android/
│   └── app/
│       ├── build.gradle             # Configuración Android con inyección de clave
│       └── src/main/
│           └── AndroidManifest.xml  # Permisos de ubicación e internet
├── ios/
│   └── Runner/
│       └── Info.plist               # Strings de permiso de ubicación (iOS)
├── pubspec.yaml                     # Dependencias del proyecto
├── .env.example                     # Template de variables de entorno
└── .gitignore                       # Archivos excluidos del control de versiones
```

---

## ⚙️ Configuración inicial

### 1. Obtener la clave de API de Google Maps

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo o selecciona uno existente
3. Habilita las siguientes APIs:
   - **Maps SDK for Android**
   - **Maps SDK for iOS**
   - **Geocoding API**
4. Ve a **Credenciales** → **Crear credenciales** → **Clave de API**
5. (Recomendado) Restringe la clave a tu app por package name / bundle ID

### 2. Configurar la clave en el proyecto

**Opción A — Archivo `.env` (recomendado):**
```bash
cp .env.example .env
# Edita .env y reemplaza TU_CLAVE_API_AQUI
```

**Opción B — `android/local.properties`:**
```properties
GOOGLE_MAPS_API_KEY=AIza...tu_clave_aqui
```

> ⚠️ **NUNCA** subas el archivo `.env` ni `local.properties` al repositorio.

### 3. Instalar dependencias

```bash
flutter pub get
```

### 4. Ejecutar la app

```bash
flutter run
```

---

## 📦 Dependencias principales

| Paquete | Versión | Propósito |
|---|---|---|
| `google_maps_flutter` | ^2.5.3 | Widget de Google Maps |
| `geolocator` | ^11.0.0 | Acceso al GPS del dispositivo |
| `geocoding` | ^3.0.0 | Geocodificación inversa |
| `permission_handler` | ^11.3.0 | Solicitud de permisos |
| `provider` | ^6.1.2 | Gestión de estado |
| `flutter_dotenv` | ^5.1.0 | Variables de entorno |
| `intl` | ^0.19.0 | Formateo de fechas |
| `http` | ^1.2.0 | Peticiones HTTP |

---

## 🏛️ Arquitectura

El proyecto sigue una arquitectura en capas limpia:

```
UI (Screens/Widgets)
        │
        ▼
   Provider (State)
        │
        ▼
   Services (Business Logic)
        │
        ▼
   Models (Data)
```

- **Models**: Entidades de datos puras, sin dependencias de Flutter
- **Services**: Lógica de negocio que interactúa con APIs externas (GPS, Geocoding)
- **Providers**: Gestión de estado reactivo con `ChangeNotifier`
- **Screens**: Páginas completas de la app
- **Widgets**: Componentes reutilizables de UI

---

## ✨ Funcionalidades

- [x] Mapa de Google Maps interactivo a pantalla completa
- [x] Geolocalización en tiempo real con alta precisión
- [x] Geocodificación inversa (coordenadas → dirección)
- [x] Panel de datos: latitud, longitud, altitud, velocidad, rumbo, precisión
- [x] Marcador personalizado de ubicación actual
- [x] Agregar marcadores al tocar prolongadamente el mapa
- [x] Cambio de tipo de mapa (Normal, Satélite, Terreno, Híbrido)
- [x] Modo seguimiento automático de la cámara
- [x] Gestión completa de permisos con UX amigable
- [x] Tema claro y oscuro automático
- [x] Pantalla de historial de ubicaciones
- [x] Copia de coordenadas al portapapeles
- [x] Cálculos geográficos (haversine, DMS, bounding box)

---

## 🔐 Permisos requeridos

### Android
```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.INTERNET" />
```

### iOS
Agregar en `Info.plist`:
- `NSLocationWhenInUseUsageDescription`
- `NSLocationAlwaysAndWhenInUseUsageDescription`

---

## 🧪 Pruebas

```bash
# Ejecutar todos los tests
flutter test

# Verificar el análisis estático
flutter analyze

# Formatear el código
dart format lib/
```

---

## 📱 Requisitos mínimos

| Plataforma | Versión mínima |
|---|---|
| Android | SDK 21 (Android 5.0) |
| iOS | iOS 12.0 |
| Flutter | 3.0.0 |
| Dart | 3.0.0 |
