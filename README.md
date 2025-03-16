# Описание
AI анализ свободных ответов опроса 

<!---# Выбор имён
Возможно 2 подхода к выделению отдельных персоналий:
 - сопоставление с заранее подготовленным списком имён
 - формирование списка имён по обрабатываемому файлу

Пусть у нас уже сформирован список имён. Тогда обрабатываемое имя может соответствовать имени из списка, если оно является частью имени из списка. Для неидентифицированных имён можно сделать список кандидатов, но это уже дополнительно. 


# Структура хранения
Excel таблица считывается в DataFrame, который затем делится на 3 части, которые обрабатываются отдельно. Для каждой таблицы нужен будет DataFrame, в который будут складываться неидентифицированные строки. Можно будет сделать так, чтобы после правок они дообрабатывались и добавлялись в статистику к уже обработанным.

Для обработки полей с фиксированным ответом будет формироваться вложенный словарь, в котором вопросам будут сопоставляться ответы, а ответам ключи.  

Промежуточные результаты удобно будет хранить в словаре, где ключ - имя, а значение - по сути json т.е. словарь в котором названия вопросов 

Итог: 
- Исходный ```DataFrame``` 
- Выборки столбцов из исходного ```DataFrame```'ы для обработки отдельных типов руководства
- Выборки строк, для которых имя не идентифицированно для отдельных типов руководства
- Промежуточные аккумулирующие структуры для сбора статистики по персоналиям относительно каждого типа руководства
- Итоговый ```DataFrame```    

Дополнительные структуры:
- Множество имён
    - Конструктор, принимающий имя файла
    - Проверка на наличие имени и уникальности: -> Optional[str]

- Множество ответов
    - Конструктор, принимающий имя файла 
    - Найти ответ

- Множество 
-->
# Необходимые структуры
Для обработки таблицы неплохо было бы создать JSON с описанием полей, и групп:
```
{
    "поля" : {
        "имя поля 1" : "тип 1",
        "имя поля 2" : "тип 2",
        ...
        "имя поля n" : "тип n" 
    },

    "группы" : {
        "имя группы 1" : [
            1,
            2,
            5,
            ...
            4
        ],
        ...
        "имя группы n" : [
            17,
            19,
            3,
            ...
            6
        ]
    }

    "объединить" : {
        "результирующее поле 1" : [
            "объединяемое поле 1",
            "объединяемое поле 2",
            ...
            "объединяемое поле k"
        ]
        ...
    }
}
```

Для классификации полей можно использовать следующие атрибуты:
- ```check``` - галочка, которая говорит о том, следует ли обрабатывать вопросы этой группы (опционально - ограничить одной на группу)
- ```name``` - имя оцениваемого человека (опционально - ограничить одним на группу)
- ```select``` - вопрос с выбором ответа
- ```number``` - вопрос со вводом числа
- ```free``` - вопрос со свободным ответом т.е. обратная связь

Первоначально для каждой группы можно сделать две таблички - отчётную и со строками, в которых не удалось идентифицировать имена (опционально - дополнение отчётной таблички после правки необработанных имён).  

Для хранения промежуточных результатов можно использовать следующую структуру (назовём её ```collector```):    
```
{
    "name 1" : {
        "question 1" : ?,
        "question 2" : ?,
        ...
        "question n" : ?
    },
    ...
    "name m" : {
        "question 1" : ?,
        "question 2" : ?,
        ...
        "question n" : ?
    }
}
```

Формат хранения ответов на вопросы ("?") будет зависеть от его типа:
- ```select``` - счётчики по вариантам ответов и общий счётчик 
    - в данном случае под вариантами ответов будут подразумеваться те ответы, которые получаются после расшифровки т.е. в нашем случае позитивная оценка/негативная оценка
- ```number``` - сумма по всем ответам и общий счётчик
- ```free``` - полный список сырых ответов на вопрос

Для типа ```name``` можно создать некоторую структуру ```name_dict```, которая будет являться словарём, в котором по набору токенов, на которые разбивается входная строка, будет выдаваться строка с именем. Все имена будут храниться в каком-то файле.  

Для типа ```select``` имеет смысл создать файл, который будет содержать тройки ```question - awswer - interpretation```. Он будет читаться в некоторую структуру ```answer_keys```, и при обработке в ```collector```'e будет автоматически находиться. 

Поскольку каждый ```collector``` напрямую связан с отдельной группой, то имеет смысл учитывать это при создании класса. Тогда можно делать обрабатываему часть ```DataFrame``` полем класса. Для последующей обработки имеет смысл проверить корректность группы и переупорядочить поля так, чтобы первым было имя, вторым   Для инициализации ```mini_collector```'ов нужно узнать тип вопроса, для этого идём ```survey_structure``` и по switch'у создаём их.

Процесс обработки строки:
1. идентификация т.е. проверка имени и флажка 
2. проходимся по вопросам


При обработке опроса просто отправляем значение поля в ```mini_collector```.

Класс должен на выходе создавать 2 сущности: таблицу обработанных данных и таблицу необработанных данных.




 


# Процесс обработки

1. Читаем табличку в ```DataFrame```
2. Создаём общие ```name_dict``` и ```answer_keys```
3. Разбиваем ```DataFrame``` на группы столбцов в соответствии с типом руководства, и для каждой группы создаём ```collector```, в котором будем собирать данные по столбцам
4. Объединение ```collector``` в общий ```DataFrame```
5. Из итогового ```DataFrame``` собираем ответы на "Общий отчёт"
 
Думаю последние два пункта можно сделать чисто работой с ```DataFrame```, а в 3 так или иначе его нужно будет ковырять и кмк проще будет преобразовать в некоторую отдельную сущность. 

Жду комментариев.






    
        