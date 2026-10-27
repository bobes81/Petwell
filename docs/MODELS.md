# Current data model

This diagram describes the implemented models; it is not a wireframe or evidence of earlier planning. Django/allauth manage the user, account/email, permissions, sessions and sites tables.

```mermaid
erDiagram
    USER ||--o{ BLOG_POST : authors
    USER o|--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : referenced_by
    USER {
        int id PK
        string username
        string email
        boolean is_staff
    }
    PRODUCT {
        int id PK
        string name
        text description
        decimal price
        string image "Cloudinary resource"
    }
    BLOG_POST {
        int id PK
        int author_id FK
        string title
        text content
        string image "optional Cloudinary resource"
        datetime created_at
    }
    ORDER {
        int id PK
        uuid public_id UK
        int user_id FK "nullable for guest"
        string full_name
        string email
        text address
        decimal total_price
        string status "pending or paid"
        string stripe_session_id UK "nullable until created"
        json stripe_checkout_payload "frozen create parameters, no secrets"
        json cart_line_tokens "identify original cart lines"
        datetime paid_at "nullable until verified"
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price "checkout snapshot"
    }
    SUBSCRIBER {
        int id PK
        string email UK
        datetime subscribed_at
    }
```

Deleting a user removes their posts and sets their orders' user link to null. Deleting an order removes its items. A product referenced by an order item cannot be deleted. Subscriber records are independent of user accounts. Reordering does not modify old records or prices and does not initiate payment.

The UUID migration first adds a nullable field, assigns a distinct value to every historical row, then enforces uniqueness/non-nullability. Historical orders become pending rather than assuming they were paid. The migration regression test exercises multiple existing rows.

Migration `0004` adds JSON snapshots without inferring missing legacy payment data. Legacy no-response/no-payload attempts get fresh keys, and legacy lines without identities are not automatically removed from carts. Admin order deletion is disabled so payable/paid orders retain their webhook/history record.
