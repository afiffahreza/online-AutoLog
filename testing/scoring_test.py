from ..AutoLog.src.scoring import Scoring

chunk1 = [
    '2023-05-20T16:24:37+07:00 {} Checking CartService Health',
    '2023-05-20T16:24:37+07:00 {} Checking CartService Health',
    '2023-05-20T16:24:37+07:00 {} GetCartAsync called with userId=08ed00c4-accd-411c-9b8c-24ab8cb4a0c5',
    '2023-05-20T16:24:34+07:00 {} GetCartAsync called with userId=a40247d2-4bd4-4c5a-b69f-8ab2d50905b3',
    '2023-05-20T16:24:30+07:00 {} AddItemAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432, productId=1YMWWN1N4O, quantity=10',
    '2023-05-20T16:24:20+07:00 {} AddItemAsync called with userId=c052cadb-3445-4b22-b68a-65d4c0a64568, productId=OLJCESPC7Z, quantity=2',
]

chunk2 = [
    '2023-05-20T17:24:37+07:00 {} Checking CartService Health',
    '2023-05-20T17:24:37+07:00 {} Checking CartService Health',
    '2023-05-20T17:24:37+07:00 {} GetCartAsync called with userId=08ed00c4-accd-411c-9b8c-24ab8cb4a0c5',
    '2023-05-20T17:24:36+07:00 {} GetCartAsync called with userId=6e6366b2-b144-4e51-a965-17cc9c89abf6',
    '2023-05-20T17:24:30+07:00 {} EmptyCartAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432',
    '2023-05-20T17:24:30+07:00 {} EmptyCartAsync called with userId=23695ecf-2bcd-4e01-a965-17cc9c89abf6',
    '2023-05-20T17:24:30+07:00 {} GetCartAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432',
]

chunk3 = [
    '2023-05-20T18:24:37+07:00 {} GetCartAsync called with userId=08ed00c4-accd-411c-9b8c-24ab8cb4a0c5',
    '2023-05-20T18:24:34+07:00 {} GetCartAsync called with userId=a40247d2-4bd4-4c5a-b69f-8ab2d50905b3',
    '2023-05-20T18:24:30+07:00 {} GetCartAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432',
    '2023-05-20T18:24:30+07:00 {} GetCartAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432',
    '2023-05-20T18:24:30+07:00 {} AddItemAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432, productId=1YMWWN1N4O, quantity=10',
    '2023-05-20T18:24:20+07:00 {} AddItemAsync called with userId=c052cadb-3445-4b22-b68a-65d4c0a64568, productId=OLJCESPC7Z, quantity=2',
]

normal = [
    '2023-05-20T18:24:37+07:00 {} Checking CartService Health',
    '2023-05-20T18:24:37+07:00 {} GetCartAsync called with userId=08ed00c4-accd-411c-9b8c-24ab8cb4a0c5',
    '2023-05-20T18:24:34+07:00 {} GetCartAsync called with userId=a40247d2-4bd4-4c5a-b69f-8ab2d50905b3',
    '2023-05-20T18:24:30+07:00 {} EmptyCartAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432',
    '2023-05-20T18:24:30+07:00 {} AddItemAsync called with userId=23695ecf-2bcd-4e01-af0b-0dd847b26432, productId=1YMWWN1N4O, quantity=10',
]

fail = [
    '2023-05-20T18:24:30+07:00 {} Checking CartService Health',
    '2023-05-20T18:24:30+07:00 {} Checking CartService Health',
    '2023-05-20T18:24:30+07:00 {} Checking CartService Health',
    '2023-05-20T18:24:30+07:00 {} info: Grpc.AspNetCore.Server.ServerCallHandler[14]',
    '2023-05-20T18:24:30+07:00 {} Error reading message.',
    '2023-05-20T18:24:30+07:00 {} System.IO.IOException: The request stream was aborted.',
]

scoring = Scoring()

scoring.add_lines(chunk1)
scoring.add_lines(chunk2)
scoring.add_lines(chunk3)

baseline_scores = scoring.calculate_baseline_score()

print(baseline_scores)

print(scoring.calculate_score(normal))
print(scoring.calculate_score(fail))
