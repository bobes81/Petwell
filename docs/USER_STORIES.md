# PetWell feature stories — implementation and acceptance tracking

This is a **retrospective Agile issue map assembled on 31 October 2026**, connecting the implemented application to its user goals, tests and assessment criteria. These GitHub Issues were created after implementation to provide an accessible, truthful review trail. They are **not original sprint tickets**, historical Kanban progress or proof that work was carried out in issue-number order.

[**GitHub Issues — all PetWell user stories**](https://github.com/bobes81/Petwell/issues?q=US-) · [**Source code**](https://github.com/bobes81/Petwell) · [**Testing evidence**](TESTING.md)

| Story | User goal / delivered feature | Priority | GitHub issue | Status and boundary |
| --- | --- | --- | --- | --- |
| US-01 | Secure hosted Stripe checkout | Must | [#10](https://github.com/bobes81/Petwell/issues/10) | Implemented; owner sandbox checkout verified |
| US-02 | Idempotent payment retries | Must | [#11](https://github.com/bobes81/Petwell/issues/11) | Implemented; isolated regression coverage |
| US-03 | Author-owned blog CRUD | Must | [#12](https://github.com/bobes81/Petwell/issues/12) | Implemented; tests and local browser checks |
| US-04 | Private pet profile CRUD | Must | [#13](https://github.com/bobes81/Petwell/issues/13) | Implemented; tests and local browser checks |
| US-05 | Private order history / Buy again | Must | [#14](https://github.com/bobes81/Petwell/issues/14) | Implemented; synthetic-history tests |
| US-06 | Account sign-in and password recovery | Must | [#15](https://github.com/bobes81/Petwell/issues/15) | **Open:** login covered; SMTP test mail received; full hosted reset link not independently verified |
| US-07 | Validated newsletter signup | Must | [#16](https://github.com/bobes81/Petwell/issues/16) | Implemented; storage/validation only |
| US-08 | SEO, robots and sitemap | Must | [#17](https://github.com/bobes81/Petwell/issues/17) | Implemented; automated tests |
| US-09 | Relevant catalogue imagery | Must | [#18](https://github.com/bobes81/Petwell/issues/18) | Image references updated; owner storefront review |
| US-10 | Responsive interface | Must | [#19](https://github.com/bobes81/Petwell/issues/19) | Local desktop/mobile evidence |
| US-11 | Facebook business-page mockup | Must | [#20](https://github.com/bobes81/Petwell/issues/20) | Clearly labelled permitted mockup |
| US-12 | Documented repeatable deployment | Must | [#21](https://github.com/bobes81/Petwell/issues/21) | README, configuration and CI |
| US-13 | Publish future marketing campaigns | Should | [#22](https://github.com/bobes81/Petwell/issues/22) | **Open:** published marketing and campaign delivery not implemented |
| US-14 | Prevent unavailable-product purchase | Must | [#23](https://github.com/bobes81/Petwell/issues/23) | Implemented; production PDF listing withdrawn |

**Assessment mapping:** each issue body identifies the relevant LO and criteria, actual user goal, implementation location and honest verification scope. Closing an issue means its described implementation deliverable is complete; it is **not** an assertion that every external-service acceptance test has passed. Independent current e-commerce provider/browser testing limits are recorded in [TESTING.md](TESTING.md).

The unrelated old workout/mood issues (#1–#7) were closed as **not planned for PetWell** on 31 October 2026; the history remains intact rather than being deleted.

