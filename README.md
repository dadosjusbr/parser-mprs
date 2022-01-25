# Ministério Público do Rio Grande do Sul (MPRS)

Este coletor tem como objetivo a recuperação de informações sobre folhas de pagamentos de funcionários a partir do Ministério Público do Rio Grande do Sul. O site com as informações pode ser acessado [aqui](https://transparencia.mprs.mp.br).

## Como usar
### Executando com Docker

 - Inicialmente é preciso instalar o [Docker](https://docs.docker.com/install/). 

 - Construção da imagem:

    ```sh
    $ cd coletores/mprs
    $ sudo docker build -t mprs .
    ```
 - Execução:
 
    ```sh
    $ sudo docker run -e YEAR=2018 -e MONTH=01 -e GIT_COMMIT=$(git rev-list -1 HEAD) mprs
    ```
### Execução sem o Docker:

- Para executar o script é necessário rodar o seguinte comando, a partir do diretório `/mprs`, adicionando às variáveis seus respectivos valores, a depender da consulta desejada. É válido lembrar que faz-se necessario ter o [Python 3.6.9](https://www.python.org/downloads/) instalado.

    ```sh
    MONTH=01 YEAR=2018 GIT_COMMIT=$(git rev-list -1 HEAD) python3 src/main.py
    ```
- Para que a execução do script possa ser corretamente executada é necessário que todos os requirements sejam devidamente instalados. Para isso, executar o [PIP](https://pip.pypa.io/en/stable/installing/) passando o arquivo requirements.txt, por meio do seguinte comando:

   ```sh
   pip install -r requirements.txt
   ```