# tokenizer.py

class Token:
    def __init__(self, tipo, valor, linea, posicion):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.posicion = posicion
    
    def __str__(self):
        return f"Token({self.tipo:20s}, '{self.valor:20s}', linea={self.linea:3d}, pos={self.posicion:3d})"


class TablaSimbolos:
    def __init__(self):
        # diccionario para guardar identificadores
        self.simbolos = {}
    
    def agregar(self, nombre, tipo, linea):
        # si no existe, lo agregamos
        if nombre not in self.simbolos:
            self.simbolos[nombre] = {
                'tipo': tipo,
                'primera_aparicion': linea
            }
    
    def mostrar(self):
        print("\n" + "="*60)
        print("TABLA DE SIMBOLOS")
        print("="*60)
        for nombre, info in self.simbolos.items():
            print(f"{nombre:30s} | tipo: {info['tipo']:15s} | linea: {info['primera_aparicion']}")


class Tokenizador:
    def __init__(self):
        # palabras reservadas de java
        self.palabras_reservadas = {
            'public', 'private', 'class', 'static', 'final', 'void',
            'int', 'double', 'String', 'if', 'else', 'return',
            'this', 'new', 'for', 'while'
        }
        
        # simbolos que reconocemos
        self.simbolos_simples = {
            '(', ')', '{', '}', '[', ']', ';', ',', '.', '=', 
            '+', '-', '*', '/', '!', '<', '>', '&', '|'
        }
        
        # operadores de dos caracteres
        self.simbolos_dobles = {
            '++', '--', '==', '!=', '<=', '>=', '&&', '||', '+=', '-='
        }
        
        self.tokens = []
        self.tabla = TablaSimbolos()
        self.linea_actual = 1
        self.pos_actual = 0
    
    def es_letra(self, c):
        # chequea si es letra o guion bajo
        return c.isalpha() or c == '_'
    
    def es_digito(self, c):
        # chequea si es numero
        return c.isdigit()
    
    def es_espacio(self, c):
        # chequea si es espacio o tab o salto de linea
        return c in ' \t\n\r'
    
    def leer_numero(self, codigo, i):
        # lee un numero entero o decimal
        inicio = i
        tiene_punto = False
        
        while i < len(codigo):
            if self.es_digito(codigo[i]):
                i += 1
            elif codigo[i] == '.' and not tiene_punto:
                tiene_punto = True
                i += 1
            else:
                break
        
        numero = codigo[inicio:i]
        tipo = 'NUMERO_DECIMAL' if tiene_punto else 'NUMERO_ENTERO'
        return numero, tipo, i
    
    def leer_identificador(self, codigo, i):
        # lee una palabra (identificador o palabra reservada)
        inicio = i
        
        while i < len(codigo) and (self.es_letra(codigo[i]) or self.es_digito(codigo[i])):
            i += 1
        
        palabra = codigo[inicio:i]
        
        # determina si es palabra reservada o identificador
        if palabra in self.palabras_reservadas:
            tipo = 'PALABRA_RESERVADA'
        else:
            tipo = 'IDENTIFICADOR'
            self.tabla.agregar(palabra, 'identificador', self.linea_actual)
        
        return palabra, tipo, i
    
    def leer_string(self, codigo, i):
        # lee una cadena de texto entre comillas
        inicio = i
        i += 1  # saltar la comilla inicial
        
        while i < len(codigo) and codigo[i] != '"':
            if codigo[i] == '\\':  # para escapar caracteres
                i += 2
            else:
                i += 1
        
        if i < len(codigo):
            i += 1  # incluir la comilla final
        
        return codigo[inicio:i], 'STRING', i
    
    def leer_comentario_linea(self, codigo, i):
        # lee comentario de una linea //
        inicio = i
        while i < len(codigo) and codigo[i] != '\n':
            i += 1
        return codigo[inicio:i], 'COMENTARIO', i
    
    def leer_comentario_bloque(self, codigo, i):
        # lee comentario de bloque /* */
        inicio = i
        i += 2  # saltar /*
        
        while i < len(codigo) - 1:
            if codigo[i] == '*' and codigo[i+1] == '/':
                i += 2
                break
            if codigo[i] == '\n':
                self.linea_actual += 1
            i += 1
        
        return codigo[inicio:i], 'COMENTARIO', i
    
    def tokenizar(self, codigo):
        i = 0
        
        while i < len(codigo):
            self.pos_actual = i
            
            # saltar espacios
            if self.es_espacio(codigo[i]):
                if codigo[i] == '\n':
                    self.linea_actual += 1
                i += 1
                continue
            
            # comentarios
            if i < len(codigo) - 1 and codigo[i:i+2] == '//':
                valor, tipo, i = self.leer_comentario_linea(codigo, i)
                self.tokens.append(Token(tipo, valor, self.linea_actual, self.pos_actual))
                continue
            
            if i < len(codigo) - 1 and codigo[i:i+2] == '/*':
                linea_inicio = self.linea_actual
                valor, tipo, i = self.leer_comentario_bloque(codigo, i)
                self.tokens.append(Token(tipo, valor, linea_inicio, self.pos_actual))
                continue
            
            # numeros
            if self.es_digito(codigo[i]):
                valor, tipo, i = self.leer_numero(codigo, i)
                self.tokens.append(Token(tipo, valor, self.linea_actual, self.pos_actual))
                continue
            
            # strings
            if codigo[i] == '"':
                valor, tipo, i = self.leer_string(codigo, i)
                self.tokens.append(Token(tipo, valor, self.linea_actual, self.pos_actual))
                continue
            
            # identificadores y palabras reservadas
            if self.es_letra(codigo[i]):
                valor, tipo, i = self.leer_identificador(codigo, i)
                self.tokens.append(Token(tipo, valor, self.linea_actual, self.pos_actual))
                continue
            
            # operadores de dos caracteres
            if i < len(codigo) - 1 and codigo[i:i+2] in self.simbolos_dobles:
                self.tokens.append(Token('OPERADOR', codigo[i:i+2], self.linea_actual, self.pos_actual))
                i += 2
                continue
            
            # simbolos simples
            if codigo[i] in self.simbolos_simples:
                self.tokens.append(Token('SIMBOLO', codigo[i], self.linea_actual, self.pos_actual))
                i += 1
                continue
            
            # caracter desconocido
            print(f"Advertencia: caracter desconocido '{codigo[i]}' en linea {self.linea_actual}")
            i += 1
        
        return self.tokens


def main():
    # leer el archivo java
    with open('tokenizador.java', 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # crear tokenizador y procesar
    tokenizador = Tokenizador()
    tokens = tokenizador.tokenizar(codigo)
    
    # mostrar tokens
    print("="*60)
    print("LISTA DE TOKENS")
    print("="*60)
    for token in tokens:
        print(token)
    
    # mostrar tabla de simbolos
    tokenizador.tabla.mostrar()
    
    # estadisticas
    print("\n" + "="*60)
    print("ESTADISTICAS")
    print("="*60)
    print(f"Total de tokens: {len(tokens)}")
    print(f"Total de identificadores unicos: {len(tokenizador.tabla.simbolos)}")


if __name__ == "__main__":
    main()
