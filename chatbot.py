from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

cache = {'estatus':0}

@app.route('/bot', methods=['POST'])
def hello_world():
    incoming_msg = request.values.get('Body', '').lower()
    print(incoming_msg)
    resp = MessagingResponse()
    msg = resp.message()

    #Saludo con cualquier entrada
    if cache['estatus'] == 0:
        cache['estatus'] = 1
        msg.body('''¡Hola! Bienvenido al chatbot de chib, las opciones son las siguientes:\n\n''' +\
            '''>Para convertir de dólar a peso mexicano, escribe 1\n\n'''+\
            '''>Para convertir de peso mexicano a dólar, escribe 2\n\n'''+\
            '''>Para salir, escribe salir (:''')
        return str(resp)

    #Salir 
    if cache['estatus'] > 0 and 'salir' in incoming_msg:
        cache['estatus'] = 0
        msg.body('''Tu sesión ha finalizado, gracias por usar nuestro chatbot :)''')
        return str(resp)

    #Leer opción seleccionada
    if cache['estatus'] == 1 and '1' == incoming_msg:
        cache['estatus'] = 2
        msg.body('''Escribe la cantidad de dólares que quieres convertir a pesos:''')
        return str(resp)
    elif cache['estatus'] == 1 and '2' == incoming_msg:
        cache['estatus'] = 3
        msg.body('''Escribe la cantidad de pesos que quieres convertir a dólares:''')
        return str(resp)
    elif cache['estatus'] == 1:
        msg.body('''La opción que intentas elegir es incorrecta :(''')
        return str(resp)

    #Leer número de entrada
    if cache['estatus'] > 1:
        try:
            quantity = float(incoming_msg)
            if quantity < 0:
                msg.body('No se permiten números negativos, intenta con otra cantidad:')
                return str(resp)

            #Llamada a API externa
            r = requests.get('https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43787/datos/oportuno', headers={'Bmx-Token':'8c000545f132ca4e3d211fbd703b5d2f2cc5f4bc655fe4ffeec964e63701ac11'})
            if r.status_code == 200:
                data = r.json()
                unit_value = r.json()['bmx']['series'][0]['datos'][0]['dato']
            else:
                msg.body('''No puedo hacer la conversión en este momento, por favor intenta más tarde.''')
                return str(resp)

            #Cálculo del resultado de acuerdo a opción
            if cache['estatus'] == 2:
                result = quantity * float(unit_value)
                result = str(round(result, 4))
                msg.body('El resultado es: ' + incoming_msg + ' USD = ' + result + ' MXN \n\nSesión terminada, hasta luego :)')
            if cache['estatus'] == 3:
                result = quantity / float(unit_value)
                result = str(round(result, 4))
                msg.body('El resultado es: ' + incoming_msg + ' MXN = ' + result + ' USD \n\nSesión terminada, hasta luego :)')
            cache['estatus'] = 0
            return str(resp)

        except:
            msg.body('''Escribe un número válido, por ejemplo: 100.50''')
            return str(resp)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)