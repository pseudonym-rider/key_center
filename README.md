# Key Center
그룹서명 키 발급, 서명을 해주는 Key Center 입니다.

## 개인 키 생성
- URI : https://key.prider.xyz/issue-key
- METHOD : POST
- request

    | key | explanation | type |
    |--- |--- |--- |
    | user_id | User id | string |
    | type | User type | string |
    
- response code
    - Header :
        Content-Type : application/json
    - SUCCESS RESPONSE
    
        | key | value | type |
        |--- |--- |--- |
        | gpk | Group public key | String |
        | usk | User private key | String |

## 개인 키 서명
- URI : https://key.prider.xyz/get-sign
- METHOD : POST
- request

    | key | explanation | type |
    |--- |--- |--- |
    | usk | User private key | string |
    | type | User type | string |
    | body | Payload | string |
    
- response code
    - Header :
        Content-Type : application/json
    - SUCCESS RESPONSE
    
        | key | value | type |
        |--- |--- |--- |
        | sign | Signed value | String |
