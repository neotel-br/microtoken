# microtoken

Microserviço de tokenização para *CipherTrust Tokenization Server*

## Uso

### FastAPI

#### Criar .env
    touch fastapi/.env

##### Variáveis
    CTS_IP=""                                                                              
    CTS_USERNAME_TOKENIZATION=""
    CTS_PASSWORD_TOKENIZATION=""
    CTS_USERNAME_DETOKENIZATION_CPF=""
    CTS_PASSWORD_DETOKENIZATION_CPF=""
    CTS_USERNAME_DETOKENIZATION_RG=""
    CTS_PASSWORD_DETOKENIZATION_RG=""
    CTS_USERNAME_DETOKENIZATION_SALARY=""
    CTS_PASSWORD_DETOKENIZATION_SALARY=""
    CTS_USERNAME_DETOKENIZATION_EMAIL=""
    CTS_PASSWORD_DETOKENIZATION_EMAIL=""
    CTS_USERNAME_DETOKENIZATION_PHONE=""
    CTS_PASSWORD_DETOKENIZATION_PHONE=""
    CTS_USERNAME_DETOKENIZATION_BANK=""
    CTS_PASSWORD_DETOKENIZATION_BANK=""
    CTS_USERNAME_DETOKENIZATION_AGENCY=""
    CTS_PASSWORD_DETOKENIZATION_AGENCY=""
    CTS_USERNAME_DETOKENIZATION_CC=""
    CTS_PASSWORD_DETOKENIZATION_CC=""
    CTS_USERNAME_DETOKENIZATION_CLEAR=""
    CTS_PASSWORD_DETOKENIZATION_CLEAR=""
    
Development:

*Make*
```console
make TARGET=fastapi dev
```

*Docker*
```console
docker-compose up
```

### Flask

Development:

```console
make TARGET=flask dev
```
