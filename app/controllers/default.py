import boto3
import requests
import uuid

from app import app

@app.route('/')
def hello_world():
    return jsonify({'Hello': 'World!'})


def search_artist(artist):
    base_url = "http://api.genius.com"
    headers = {'Authorization': 'Bearer ha74ReWOEDeHHz6Y7jMi2Fy_u3-i7Rip7CK9hvVoC1TnoOZdhRxtSPhfJwN4HUSn'}
    search_url = "{}/search?q={}".format(base_url, artist)
    return requests.get(search_url, headers=headers).json()


def top_hits(info_artist):
    list_songs = []
    for song in info_artist['response']['hits']:
        list_songs.append(song['result']['title'])
    return list_songs


def cache_available(artist):
    # redis.
    # ver se o artista está em cache
    # se sim = recupera as informações e atualiza no dynamo
    # se não continua no fluxo para salvar no redis
    client = boto3.client('elasticache')
    client.create_cache_cluster(
        CacheClusterId='string',
        ReplicationGroupId='string',
    )
    return False


def clear_cache():
    pass


@app.route('/artista')
def artist():
    artist = request.args.get('nome', '')
    cache = request.args.get('cache', 'True')

    if cache is True:
        print('CACHEADO')
        if cache_available(artist) is True:
            return jsonify()
    else:
        clear_cache()

    res = search_artist(artist)

    id_transaction = ''
    if len(res['response']['hits']) != 0:
        id_transaction = str(uuid.uuid4())

    hits = top_hits(res)

    about = {
        'id_transaction': id_transaction,
        'artist': artist,
        'songs': hits
    }
    print(about)


    if about['id_transaction'] == '':
        return jsonify(about)

    # salvar duplicado??

    dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id='AKIAYC7NMOQEBMEBML2Z',
        aws_secret_access_key='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'
        )

    table = dynamodb.Table('tb_searches')

    response = table.put_item(
        Item={
            'id_transaction': id_transaction,
            'artist': artist,
            'songs': hits
        }
    )


    # import pdb; pdb.set_trace()

    # dynamodb = boto3.resource('dynamodb')


    return jsonify(about)