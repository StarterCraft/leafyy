/**
*
* @param obj {object} объект со значениями перечисления
*/
function Enum(obj) {
    // итоговый объект
    const newObj = {};

    // проходимся по каждому свойству переданного в функцию объекта
    for( const prop in obj )
    {
        // проверяем наличие собственного свойства у объекта
        if (obj.hasOwnProperty(prop)) {

            // помещаем в новый объект специальный примитивный тип JavaScript Symbol
            newObj[prop] = Symbol(obj[prop]);
        }
    }

    // делаем объект неизменяемым (свойства объекта нельзя будет изменить динамически)
    return Object.freeze(newObj);
}

function reportStdCallback(request) {
    if (request.status > 299)
        console.warn(request.responseText);

    onUpdateConsoleData();
}

function report(level, message, callback = reportStdCallback) {
    const levels = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ];

    level = level.toUpperCase();
    if (!levels.includes(level)){
        throw SyntaxError("Unsupported level: " + level);
}
    var xmlHttp = new XMLHttpRequest();

    xmlHttp.onreadystatechange = () => callback(xmlHttp);

    xmlHttp.open("POST", "/log", true); // true for asynchronous

    // Send the proper header information along with the request
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    const d = {
        "level": level, 
        "message": message
    };

    xmlHttp.send(JSON.stringify(d));
}
