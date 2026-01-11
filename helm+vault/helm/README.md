# Foodgram Helm Chart

Helm chart для развертывания приложения Foodgram в Kubernetes. Включает все необходимые компоненты: базу данных PostgreSQL, backend на Django, frontend на React и Nginx в качестве reverse proxy.

## Структура

Чарт состоит из следующих подчартов:

- **db** - PostgreSQL StatefulSet с репликацией
- **backend** - Django приложение с миграциями и сборкой статики
- **frontend** - React приложение
- **nginx** - Reverse proxy и статические файлы

## Установка

### Базовая установка

```bash
helm install foodgram . -n foodgram --create-namespace
```

### С кастомными значениями

```bash
helm install foodgram . -f my-values.yaml -n foodgram --create-namespace
```

### Обновление

```bash
helm upgrade foodgram . -n foodgram
```

### Удаление

```bash
helm uninstall foodgram -n foodgram
```

## Конфигурация

### Основные параметры (values.yaml)

```yaml
global:
  secret:
    name: "db-secrets"  # Имя секрета для БД

ingress:
  serviceName: nginx-service  # Имя сервиса для ingress
  servicePort: 80
  tlsSecret: foodgram-tls  # Имя TLS секрета
  hosts:
    - foodgram.loc
    - alhost.ru
```

### Подчарты

Все подчарты включены по умолчанию. Можно отключить любой через условия:

```yaml
db:
  enabled: true
backend:
  enabled: true
frontend:
  enabled: true
nginx:
  enabled: true
```

#### Backend

Основные настройки находятся в `charts/backend/values.yaml`:

- Реплики: 3
- Образ: `mrilki/foodgram_backend:latest`
- Порты: 80 -> 8000
- Хранилища: collected-static (200Mi), media (2Gi)
- Миграции выполняются через Job перед запуском

#### Database

Настройки БД в `charts/db/values.yaml`:

- Реплики: 2 (StatefulSet)
- Образ: `bitnami/postgresql:latest`
- Хранилище: 1Gi на каждый под
- Replication включена

#### Frontend

Настройки фронтенда в `charts/frontend/values.yaml`:

- Реплики: 1
- Образ: `mrilki/foodgram_frontend:latest`
- Хранилище: 1Gi для статики
- Сборка происходит в initContainer

#### Nginx

Настройки в `charts/nginx/values.yaml`:

- Реплики: 1
- Образ: `nginx:1.25.4-alpine`
- Проксирует `/api/` и `/admin/` на backend
- Раздает статику и медиа файлы

## Важные моменты

1. **Секреты БД**: backend использует секрет `db-secrets`, который создается подчартом `db`. Убедитесь что имя совпадает.

2. **PVC имена**: nginx ссылается на PVC из других подчартов:
   - `frontend-static-pvc` - статика фронтенда
   - `backend-collected-pvc` - собранная статика Django
   - `backend-media-pvc` - медиа файлы

3. **Имена сервисов**: nginx проксирует на `backend-service` (полное имя формируется через fullnameOverride).

4. **Миграции**: выполняются через Job перед запуском backend. Если нужно перезапустить миграции - удалите Job.

5. **Хранилища**: используются hostPath volumes (для продакшена лучше использовать StorageClass).

## Проверка установки

```bash
# Проверить статус подов
kubectl get pods -n foodgram

# Проверить сервисы
kubectl get svc -n foodgram

# Проверить PVC
kubectl get pvc -n foodgram

# Логи backend
kubectl logs -n foodgram -l app.kubernetes.io/name=backend --tail=100

# Логи миграций
kubectl logs -n foodgram -l app.kubernetes.io/name=backend -c migrations
```

## Troubleshooting

**Поды не запускаются:**
- Проверьте логи: `kubectl describe pod <pod-name> -n foodgram`
- Убедитесь что PVC созданы и примонтированы
- Проверьте что секреты существуют

**Миграции падают:**
- Проверьте подключение к БД
- Посмотрите логи Job миграций
- Убедитесь что секреты БД правильные

**Nginx не проксирует:**
- Проверьте что backend-service существует и доступен
- Проверьте ConfigMap nginx: `kubectl get configmap nginx-config -n foodgram -o yaml`

**Статика не отдается:**
- Проверьте что PVC примонтированы в nginx
- Убедитесь что collectstatic выполнился успешно
- Проверьте пути в nginx конфигурации

## Разработка

Для разработки можно запускать отдельные подчарты:

```bash
# Только БД
helm install db charts/db -n foodgram --create-namespace

# Обновить зависимости после изменения подчартов
helm dependency update
```

## Версии

- Chart version: 0.1.0
- App version: 1.16.0
