# Current data model

This diagram describes the implemented models; it is not a wireframe or evidence of earlier planning. Django/allauth manage the user, account/email, permissions, sessions and sites tables.

```mermaid
erDiagram
    USER ||--o{ BLOG_POST : authors
    USER ||--o{ PET_PROFILE : owns
    ORDER o|--o{ CHECKOUT_STATE : active_attempt
    USER o|--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : referenced_by
    USER {
        int id PK
        string username
        string email
        boolean is_staff
    }
    PET_PROFILE {
        int id PK
        int owner_id FK
        string name
        string species
        string care_focus
        text notes "optional, max500"
    }
    CHECKOUT_STATE {
        string session_digest PK
        int active_order_id FK "nullable"
        uuid processing_token "nullable lease holder"
        datetime processing_until "nullable lease expiry"
    }
    PRODUCT {
        int id PK
        string name
        text description
        decimal price
        string image "Cloudinary resource"
        boolean is_available "default True; explicit reviewed withdrawal"
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

Deleting a user removes their posts and pet profiles and sets their orders' user link to null. Deleting an order removes its items, but an order referenced by a CheckoutState cannot be deleted because that foreign key is protected. A product referenced by an order item also cannot be deleted. Subscriber records are independent of user accounts. Reordering does not modify old records or prices and does not initiate payment. The admin additionally disables order deletion, including records not currently referenced by a checkout coordinator.

The UUID migration first adds a nullable field, assigns a distinct value to every historical row, then enforces uniqueness/non-nullability. Historical orders become pending rather than assuming they were paid. The migration regression test exercises multiple existing rows.

Migration `0004` adds JSON snapshots without inferring missing legacy payment data. Legacy no-response/no-payload attempts get fresh keys, and legacy lines without identities are not automatically removed from carts. Admin order deletion is disabled so payable/paid orders retain their webhook/history record.

`accounts.0001` creates the owner-only PetProfile model and frontend feature. `orders.0005` creates CheckoutState: an internal session-scoped lease/pointer, not a substitute for the user-facing custom model. API I/O occurs outside the short database transaction; expired leases can recover durable order snapshots.

`products.0002` adds availability without automatically withdrawing a row. Catalogue/direct cart/stale cart/checkout/reorder reject withdrawn or nonpositive-priced items; OrderItems and legitimate signed payment confirmation remain intact. The later actual six-migration real-backup rehearsal and owner-verified 30 October production application now complete the schema/migration check. Actual exact-row PDF withdrawal remains separate and unverified; [deployment evidence](evidence/30oct-production-deployment.md).
