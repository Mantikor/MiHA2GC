[![GitHub Clones](https://img.shields.io/badge/dynamic/json?color=success&label=Clone&query=count&url=https://gist.githubusercontent.com/Mantikor/11d1e1d5c906379d6a356c2aee061ed2/raw/clone.json&logo=github)](https://github.com/MShawon/github-clone-count-badge)

![](mi2gc.png)

# Набор программ, которые реализуют интеграцию весов Xiaomi в экосистему Garmin.

## Поддерживаются весы: **Xiaomi Mi Smart Scale 2 (XMTZC04HM)**, **Xiaomi Mi Body Composition Scale 2 (XMTZC05HM)** (тестировались)

Все это началось из-за лени каждый раз при взвешивании запускать программу, которая ловит по BT данные от весов и передает их в контейнер, в котором крутится [Yet Another Garmin Connect Client](https://github.com/lswiderski/yet-another-garmin-connect-client). Я долгое время так делал в экосистеме **Huawei**. А потом купил весы **Huawei Scale 3**, которые умеют подключаться по WiFi и жизнь стала проще: взвесился и данные сразу в аккаунте. К этому я быстро привык. И вот момент перехода в экосистему **Garmin**. Очень не хотелось покупать их дорогие весы. Весы **Huawei** удалось прикрутить, но нужно было пройти такой путь: **Huawei Health -> Health Sync -> Fitbit -> MyFitnessPal -> Garmin Connect**, к тому же синхронизировался только вес. Не то чтобы мне сильно нужно было что то еще, но, смотрите выше, в **Scale 3** был набор дополнительных данных кроме веса. Далее я достал свои старые **Xiaomi Mi Smart Scale 2 (XMTZC04HM)**. Получилось подключить их через программу и при взвешивании данные передавались в **Garmin Connect**. Конечно, передавался только вес, больше они ничего не умеют. И в принципе, кому такого варианта (с запуском программы) достаточно, вы можете дальше не читать, а узнать MAC адрес весов, [скачать программу](https://github.com/lswiderski/mi-scale-exporter) и настроить экспорт через нее.

Кому же лень, как и мне, каждый раз запускать программу для экспорта, читаем далее, пробуем и если все получится и понравится ставим звёзды, лайки и т.д. Если что то не работает, то создаем PR, будем разбираться.

Нам понадобятся весы **Xiaomi**, которые интегрированы в Home Assistant, и два контейнера с программами (один для расчета данных по импедансу и весу, второй для передачи этих данные в **Garmin Connect**). Все это у меня крутится на домашнем сервере.

Итак, далее я обновил весы на **Xiaomi Mi Body Composition Scale 2 (XMTZC05HM)**, которые умеют не только вес. У меня в квартире давно работает **Home Assistant**, поэтому какое то количество устройств, которые позволяют это сделать, интегрировано в него. Сначала был подвязан чайник **Redmond** через Bluetooth шлюз на базе ESP32. [Ссылка на проект](https://github.com/alutov/ESP32-R4sGate-for-Redmond). Данные с устройства уходят на MQTT сервер и через интеграцию MQTT попадают в **Home Assistant**. Если на сервере у вас есть адаптер Bluetooth, то можно настроить интеграцию для весов, которая есть в самом **Home Assistant**. Но, кажется, она не умеет передавать импеданс, а только вес. Предположу, что можно использовать **Xiaomi S400** и [интеграцию от AlexxIT](https://github.com/AlexxIT/XiaomiGateway3) для получения данных веса и импеданса в **Home Assistant**.

Как только разобрались с подключением весов к **Home Assistant**, вы будете иметь сущности (entity): **вес, импеданс, дата, время**.

### Настраиваем configuration.yaml в Home Assistant

В **HA**, в файл **configuration.yaml** нужно добавить следующую строку:

```
rest_command: !include rests.yaml
```

эта строка должна быть перед строкой подключения автоматизаций и выглядеть это будет так:

```
rest_command: !include rests.yaml
automation: !include automations.yaml
```

### Содержимое файла **rests.yaml**:

```
send_weight_to_gc:
  url: http://server_ip:server_port/update?weight={{ weight }}&impedance={{ impedance }}
  method: get
```

где **server_ip** и **server_port** - ip адрес и port сервера, где будет развернуты контейнеры для пересчета веса и импеданса и отправки данных в **GC**.

Например:

```
send_weight_to_gc:
  url: http://192.168.1.111:6999/update?weight={{ weight }}&impedance={{ impedance }}
  method: get
```

Там же, в **HA**, вам нужно создать автоматизацию, которая по изменению даты или времени вызовет описанную выше REST команду:

```
alias: MiHA2GC
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.mi2scale_xxxxxxxxxx_date
      - sensor.mi2scale_xxxxxxxxxx_time
conditions: []
actions:
  - action: rest_command.send_weight_to_gc
    data:
      weight: "{{ states(\"sensor.mi2scale_xxxxxxxxxx_weight\") | float }}"
      impedance: "{{ states(\"sensor.mi2scale_xxxxxxxxxx_impedance\") | int }}"
mode: single
```

Осталось клонировать репозиторий, настроить **.env** файл и запустить сервисы.

### Пример файла **.env**:

```
API_PORT=60999
YAGCC_PORT=1280
GC_USER=your.garmin.account@gmail.com
GC_PASS=your.gc.password
GC_API=http://192.168.1.111:1280/upload
MAX_W=85
MIN_W=70
BIRTH=11-02-1978
SEX=male
HEIGHT=180
```

**API_PORT** - порт, на котором запустится сервис для пересчета веса и импеданса

**YAGCC_PORT** - порт сервиса для отправки данных в GC

**GC_USER** - ваш логин в GC

**GC_PASS** - ваш пароль в GC

**GC_API** - API эндпоинт YAGCC контейнера, для отправки данных в GC, фрмат: http://**yagcc_server_ip_address:yagcc_port**/upload где yagcc_server_ip_address - ip адрес сервера, где развернут YAGCC контейнер, yagcc_port - порт, указанный в YAGCC_PORT

**MAX_W** - максимальный порог веса

**MIN_W** - минимальный порог веса

**BIRTH** - дата рождения в формате дд-мм-гггг

**SEX** - пол, может быть male или female

**HEIGHT** - ваш рост

**.env** файл никуда не передается.

Если порты не пересекаются с портами сервисов, которые есть у вас на сервере, то рекомендуется оставить порты как есть в **.env** файле и заполнить только ваши личные данные и ip address сервера.

### Клонирование репозитория и запуск сервисов

```
# клонируем репозиторий
git clone https://github.com/Mantikor/MiHA2GC

# смена рабочей папки
cd MiHA2GC/

# редактируем .env файл, как показано выше, можно редакимровать любым способом, не обязательно через vi
vi .env

# запускаем сервисы, на этом шаге скачается образ YAGCC и соберется контейнер с сфотом для расчета данных и запустятся сервисы
docker compose up -d

# после запуска можно посмотреть логи
docker logs -f miha2gc-mi2gc_api
```

### Код для расчёта дополнительных данных по весу и импедансу взят [отсюда](https://github.com/RobertWojtowicz/export2garmin).

### Отдельное спасибо пользователю [fillinn](https://4pda.to/forum/index.php?showuser=156669) за подсказку по входящему форматe данных для YAGCC.

### Пример лога

```
[2025-01-26 10:14:18,485.485] INFO [140353679063936] - 192.168.1.111:33242 - "GET /update?weight=79.55&impedance=444 HTTP/1.1" 307
[2025-01-26 10:14:18,488.488] INFO [140353679063936] - my.awesome.gc.account@gmail.com, height: 180, age: 46
[2025-01-26 10:14:18,488.488] INFO [140353679063936] - {
  "weight": 79.55,
  "unix-timestamp": 1737875658487,
  "email": "my.awesome.gc.account@gmail.com",
  "password": "************",
  "percentFat": 23.6737649277184,
  "percentHydration": 52.35979725958518,
  "bonemass": 3.0929047416000004,
  "muscleMass": 57.624615258400006,
  "visceralFatRating": 15.537249999999997,
  "physiqueRating": 2,
  "metabolicAge": 34.825655,
  "bodyMassIndex": 24.55246913580247,
  "datetime": "2025-01-26 10:14:18"
}
[2025-01-26 10:14:23,207.207] INFO [140353679063936] - HTTP Request: POST http://192.168.1.111:1280/upload "HTTP/1.1 201 Created"
[2025-01-26 10:14:23,208.208] INFO [140353679063936] - 201
[2025-01-26 10:14:23,208.208] INFO [140353679063936] - 192.168.1.111:33242 - "GET /update/?weight=79.55&impedance=444 HTTP/1.1" 200
```

## English maybe will be
