# Key Center
그룹서명 키 발급, 서명을 해주는 Key Center 입니다.

## 개인 키 생성
- URI : https://key.prider.xyz/issue-key
- METHOD : GET
- request
    - Header :
        - Authorization: Bearer <Access token>
    - body: 
        - | key | explanation | type |
          |--- |--- |--- |
          | type | User type | string |
    
- response code
    - SUCCESS RESPONSE
    - Header
      - Content-type: application/json
    - body
      - | key | value | type |
        |--- |--- |--- |
        | gpk | Group public key | String |
        | usk | User private key | String |

## QR인증
- URI : https://key.prider.xyz/receive-qr
- METHOD : POST
- request
    - Header
      - Content-type: application/json
    - body
      - | key | explanation | type |
        |--- |--- |--- |
        | user_token | JWT access token | string |
        | store_token | JWT access token | string |
        | time | Current time | string |
        | user_secret | user private key | string |
        | store_secret | store private key | string |
    
- response code
    - SUCCESS RESPONSE
    - Header
      - Content-type: application/json
    - body
      - | key | value | type |
        |--- |--- |--- |
        | response | True | String |

## 상점 id list 가져오기
- URI : https://key.prider.xyz/get-store
- METHOD : POST
- request
    - Header
      - Content-type: application/json
      - Authorization: Bearer <Access token>
    - body
      - | key | explanation | type |
        |--- |--- |--- |
        | user_id | user_id | string |
        
- response code
    - SUCCESS RESPONSE
    - Header
      - Content-type: application/json
    - body(ex)
      - [
        
            {
                "store_id": "ghdrlfehd123",
                "time": "1608277380"
            },
            {
                "store_id": "ghdrlfehd123",
                "time": "1608277572"
            },
            {
                "store_id": "Null",
                "time": "1608277666"
            },
            {
                "store_id": "Null",
                "time": "1608277681"
            },
            {
                "store_id": "Null",
                "time": "1608277696"
            }
        ]
    
## 방문자 찾기
 URI : https://key.prider.xyz/get-store
- METHOD : POST
- request
    - Header
      - Content-type: application/json
      - Authorization: Bearer <Access token>
    - body(ex)
    - {
      
          "data": [
              
            {
                "store_id": "ghdrlfehd123",
                "time": "1608277380"
            },
            {
                "store_id": "ghdrlfehd123",
                "time": "1608277572"
            },
            {
                "store_id": "Null",
                "time": "1608277666"
            },
            {
                "store_id": "Null",
                "time": "1608277681"
            },
            {
                "store_id": "Null",
                "time": "1608277696"
            }
          ]
        }
      
- response code
    - SUCCESS RESPONSE
    - Header
      - Content-type: application/json
    - body(ex)
    - 
  {
    [
  
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277380",
            "user_id": "dldmsvy1010"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277572",
            "user_id": "dldmsvy1010"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277666",
            "user_id": "Null"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277681",
            "user_id": "Null"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277696",
            "user_id": "Null"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277380",
            "user_id": "dldmsvy1010"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277572",
            "user_id": "dldmsvy1010"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277666",
            "user_id": "Null"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277681",
            "user_id": "Null"
        },
        {
            "store_id": "ghdrlfehd123",
            "time": "1608277696",
            "user_id": "Null"
        }
      ]
  }