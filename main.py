# Tarefa de Programação – Compressão de Huffman
#
# Aluno: Antônio Lauriano de Souza Monte
#
# Para comprimir: python main.py -c -f <arquivo>.txt
#
# Para descomprimir: python main.py -d -f <arquivo>.txt.huff
#
# Para realizar a analise de frequência e imprimir tabela de simbolos: python main.py -s -f <arquivo>.txt.huff


import heapq
import os
import sys


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(data):
    frequency_table = {}
    for char in data:
        frequency_table[char] = frequency_table.get(char, 0) + 1
    return frequency_table


def build_huffman_tree(frequency_table):
    heap = []
    for char, freq in frequency_table.items():
        heapq.heappush(heap, HuffmanNode(char, freq))

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)

    if len(heap) == 0:
        print('Erro: nenhum símbolo encontrado para construir a árvore de Huffman.')
        return None
    return heap[0]


def build_encoding_table(huffman_tree):
    encoding_table = {}

    def build_encoding_helper(node, code):
        if node is None:
            return
        if node.char is not None:
            encoding_table[node.char] = code
        build_encoding_helper(node.left, code + '0')
        build_encoding_helper(node.right, code + '1')

    build_encoding_helper(huffman_tree, '')
    return encoding_table


def compress_file(input_file, output_file):
    with open(input_file, 'rb') as file:
        data = file.read().rstrip()

    frequency_table = build_frequency_table(data)
    huffman_tree = build_huffman_tree(frequency_table)
    encoding_table = build_encoding_table(huffman_tree)
    encoded_data = ''.join(encoding_table[char] for char in data)
    padding = 8 - len(encoded_data) % 8
    encoded_data += '0' * padding

    byte_array = bytearray()
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i + 8]
        byte_array.append(int(byte, 2))

    with open(output_file, 'wb') as file:
        file.write(bytes([padding]))
        file.write(byte_array)

    print(f'Arquivo comprimido salvo como {output_file}')


def decompress_file(input_file, encoding_table=None):
    if encoding_table is None:
        print('Erro: a tabela de codificação não foi fornecida.')
        return

    output_file = input_file[:-5]  # Removendo a extensão ".huff"

    with open(input_file, 'rb') as file:
        padding = int.from_bytes(file.read(1), byteorder='big')
        encoded_data = file.read()

    encoded_data = ''.join(format(byte, '08b') for byte in encoded_data)
    encoded_data = encoded_data[:-padding]

    current_code = ''
    decoded_data = ''
    for bit in encoded_data:
        current_code += bit
        if current_code in encoding_table:
            char = encoding_table[current_code]
            decoded_data += char
            current_code = ''

    with open(output_file, 'w', encoding='utf-8', errors='replace') as file:
        file.write(decoded_data)

    print(f'Arquivo descomprimido salvo como {output_file}')


def analyze_frequency(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = file.read().rstrip()

    frequency_table = build_frequency_table(data)

    print('Análise de frequência:')
    print('-------------------')
    print('Símbolo\tFrequência')
    print('------\t---------')
    for symbol, freq in frequency_table.items():
        print(f'{symbol}\t{freq}')


def calculate_compression_ratio(original_size, compressed_size):
    if original_size == 0:
        print('Erro: o tamanho do arquivo original é zero.')
        return None

    ratio = (compressed_size / original_size) * 100
    return ratio


def print_help():
    print('Compressão de Huffman – Análise de frequência símbolos e compressão de Huffman')
    print('Uso: huff [-options] <file>')
    print('Opções:')
    print('-h\tMostra este texto de ajuda')
    print('-c\tRealiza a compressão')
    print('-d\tRealiza a descompressão')
    print('-s\tRealiza apenas a análise de frequência e imprime a tabela de símbolos')
    print(
        '-f <file>\tIndica o arquivo a ser processado (comprimido, descomprimido ou para apresentar a tabela de símbolos)')


def main():
    if len(sys.argv) < 3:
        print_help()
        return

    option = sys.argv[1]
    input_file = None
    output_file = None

    if option == '-h':
        print_help()
        return
    elif option == '-c':
        if len(sys.argv) == 4 and sys.argv[2] == '-f':
            input_file = sys.argv[3]
            output_file = input_file + '.huff'
        else:
            print('Erro: argumentos inválidos.')
            print_help()
            return
    elif option == '-d':
        if len(sys.argv) == 4 and sys.argv[2] == '-f':
            input_file = sys.argv[3]
            if input_file.endswith('.huff'):
                encoding_table = build_encoding_table(
                    build_huffman_tree(build_frequency_table(open(input_file, 'rb').read().rstrip())))
                decompress_file(input_file, encoding_table)
            else:
                print('Erro: o arquivo de entrada não parece ser um arquivo comprimido.')
                return
        else:
            print('Erro: argumentos inválidos.')
            print_help()
            return
    elif option == '-s':
        if len(sys.argv) == 4 and sys.argv[2] == '-f':
            input_file = sys.argv[3]
            frequency_table = build_frequency_table(open(input_file, 'r', encoding='utf-8').read().rstrip())
            encoding_table = build_encoding_table(build_huffman_tree(frequency_table))
            print('Tabela de Frequência:')
            print('---------------')
            for symbol, code in encoding_table.items():
                print(f'{symbol}\t{code}')
        else:
            print('Erro: argumentos inválidos.')
            print_help()
            return
    else:
        print('Erro: opção inválida.')
        print_help()
        return

    if option == '-c':
        compress_file(input_file, output_file)
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(output_file)
        compression_ratio = calculate_compression_ratio(original_size, compressed_size)
        print(f'Taxa de compressão: {compression_ratio}%')


if __name__ == '__main__':
    main()
