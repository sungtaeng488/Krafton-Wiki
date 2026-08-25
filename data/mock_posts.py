from datetime import datetime


MOCK_POSTS = [
    {
        "id": 1,
        "slug": "quick-sort",
        "title": "Quick Sort",

        "summary": "Pivot을 기준으로 데이터를 나누어 정렬하는 분할 정복 알고리즘입니다.",

        "content": """
Quick Sort는 하나의 값을 Pivot으로 선택하고, Pivot보다 작은 값과 큰 값을 나누는 과정을 반복하여 정렬하는 알고리즘입니다.

배열을 두 부분으로 나눈 뒤 각각에 대해 다시 Quick Sort를 수행하는 분할 정복 방식으로 동작합니다.

평균 시간 복잡도는 O(n log n)이지만, Pivot을 계속 좋지 않게 선택하면 최악의 경우 O(n²)까지 증가할 수 있습니다.

추가적인 배열을 크게 사용하지 않고 제자리 정렬이 가능하다는 장점이 있으며, 실제 환경에서도 빠른 정렬 알고리즘 중 하나로 많이 활용됩니다.
""",

        "tags": ["알고리즘", "정렬", "분할정복"],
        "author": "성현",
        "created_at": datetime(2026, 8, 25, 20, 15),
        "likes": 32,
        "comments": 5,
        "views": 120,
        "views_24h": 85,
    },

    {
        "id": 2,
        "slug": "dfs-bfs",
        "title": "DFS와 BFS",

        "summary": "깊이 우선 탐색과 너비 우선 탐색의 차이와 상황별 선택 기준을 알아봅니다.",

        "content": """
DFS와 BFS는 그래프나 트리 구조에서 노드를 탐색하기 위한 대표적인 알고리즘입니다.

DFS는 하나의 경로를 가능한 깊게 탐색한 뒤 더 이상 진행할 수 없으면 이전 위치로 돌아가 다른 경로를 탐색합니다. 일반적으로 재귀 함수나 Stack을 사용하여 구현할 수 있습니다.

BFS는 현재 위치에서 가까운 노드부터 순서대로 탐색합니다. Queue를 이용해 구현하며, 가중치가 없는 그래프에서 최단 거리를 구할 때 유용합니다.

모든 경로를 확인하거나 백트래킹과 결합하는 문제에는 DFS가 자주 사용되고, 최단 거리나 단계별 탐색이 필요한 문제에는 BFS가 자주 사용됩니다.
""",

        "tags": ["알고리즘", "그래프", "탐색"],
        "author": "민지",
        "created_at": datetime(2026, 8, 25, 14, 20),
        "likes": 47,
        "comments": 100,
        "views": 238,
        "views_24h": 120,
    },

    {
        "id": 3,
        "slug": "tcp-three-way-handshake",
        "title": "TCP 3-Way Handshake",

        "summary": "TCP에서 클라이언트와 서버가 신뢰할 수 있는 연결을 생성하는 과정을 설명합니다.",

        "content": """
TCP는 데이터를 전송하기 전에 클라이언트와 서버 사이의 연결 상태를 확인합니다. 이때 사용하는 과정이 3-Way Handshake입니다.

먼저 클라이언트가 서버에게 SYN 패킷을 전송하여 연결을 요청합니다.

서버가 요청을 받으면 SYN과 ACK를 함께 클라이언트에게 보내 연결 요청을 확인하고 서버도 연결할 준비가 되었음을 알립니다.

마지막으로 클라이언트가 ACK를 서버에게 보내면 연결이 성립됩니다.

이 과정을 통해 양쪽 모두 데이터를 정상적으로 주고받을 준비가 되어 있는지 확인할 수 있습니다.
""",

        "tags": ["네트워크", "TCP", "통신"],
        "author": "준호",
        "created_at": datetime(2026, 8, 25, 10, 10),
        "likes": 28,
        "comments": 40,
        "views": 164,
        "views_24h": 150,
    },

    {
        "id": 4,
        "slug": "deadlock",
        "title": "Deadlock",

        "summary": "프로세스들이 서로 자원을 기다리면서 무한히 대기하게 되는 교착 상태를 알아봅니다.",

        "content": """
Deadlock은 둘 이상의 프로세스가 서로 필요한 자원을 가지고 있으면서 상대방의 자원이 반환되기를 기다려 더 이상 진행할 수 없는 상태입니다.

Deadlock이 발생하기 위해서는 상호 배제, 점유와 대기, 비선점, 순환 대기의 네 가지 조건이 동시에 만족되어야 합니다.

운영체제에서는 이러한 조건 중 하나가 발생하지 않도록 하여 Deadlock을 예방하거나, Banker's Algorithm과 같은 방법으로 안전한 상태를 유지하며 회피할 수 있습니다.

또한 Deadlock 발생을 허용한 뒤 주기적으로 탐지하고 프로세스를 종료하거나 자원을 회수하는 방법도 사용할 수 있습니다.
""",

        "tags": ["운영체제", "동시성", "교착상태"],
        "author": "지수",
        "created_at": datetime(2026, 8, 24, 15, 30),
        "likes": 51,
        "comments": 10,
        "views": 302,
        "views_24h": 60,
    },

    {
        "id": 5,
        "slug": "hash-table",
        "title": "Hash Table",

        "summary": "Key를 이용해 데이터를 빠르게 저장하고 조회할 수 있는 자료구조입니다.",

        "content": """
Hash Table은 Key를 Hash Function에 입력하여 얻은 Hash 값을 이용해 데이터를 저장하는 자료구조입니다.

적절한 Hash Function을 사용하면 데이터를 평균적으로 O(1)의 시간 복잡도로 삽입하거나 조회할 수 있습니다.

하지만 서로 다른 Key가 같은 위치를 가리키는 Hash Collision이 발생할 수 있습니다.

대표적인 충돌 해결 방법으로는 같은 위치에 여러 데이터를 연결하는 Chaining 방식과 다른 빈 공간을 찾아 저장하는 Open Addressing 방식이 있습니다.

빠른 검색 성능 때문에 Dictionary, Cache, 데이터베이스 등 다양한 시스템에서 활용됩니다.
""",

        "tags": ["자료구조", "해시", "탐색"],
        "author": "도윤",
        "created_at": datetime(2026, 8, 23, 11, 0),
        "likes": 39,
        "comments": 20,
        "views": 187,
        "views_24h": 30,
    },

    {
        "id": 6,
        "slug": "merge-sort",
        "title": "Merge Sort",

        "summary": "배열을 나눈 뒤 정렬된 결과를 다시 합치는 분할 정복 기반 정렬 알고리즘입니다.",

        "content": """
Merge Sort는 배열을 더 이상 나눌 수 없을 때까지 절반으로 나누고, 다시 두 배열을 비교하면서 정렬된 형태로 합치는 알고리즘입니다.

분할 과정과 병합 과정을 반복하며 전체 데이터를 정렬합니다.

시간 복잡도는 입력 데이터의 상태와 관계없이 O(n log n)을 유지한다는 특징이 있습니다.

또한 같은 값을 가진 데이터의 기존 순서를 유지할 수 있는 안정 정렬입니다.

다만 병합 과정에서 추가적인 메모리 공간이 필요하다는 단점이 있습니다.
""",

        "tags": ["알고리즘", "정렬", "재귀"],
        "author": "서연",
        "created_at": datetime(2026, 8, 22, 13, 0),
        "likes": 24,
        "comments": 8,
        "views": 142,
        "views_24h": 22,
    },

    {
        "id": 7,
        "slug": "process-thread",
        "title": "Process와 Thread",

        "summary": "프로세스와 스레드의 차이와 각각의 메모리 및 자원 공유 방식을 비교합니다.",

        "content": """
Process는 실행 중인 프로그램의 하나의 독립적인 실행 단위입니다.

각 Process는 Code, Data, Heap, Stack 등의 메모리 영역을 가지며 다른 Process와 기본적으로 독립된 메모리 공간을 사용합니다.

Thread는 하나의 Process 내부에서 실행되는 작업 단위입니다. 같은 Process에 속한 Thread들은 Code, Data, Heap 영역을 공유하지만 각자 Stack 영역을 가지고 있습니다.

Thread 간 데이터 공유는 빠르지만 동시에 같은 데이터에 접근할 경우 Race Condition과 같은 문제가 발생할 수 있기 때문에 동기화가 중요합니다.
""",

        "tags": ["운영체제", "프로세스", "스레드"],
        "author": "현우",
        "created_at": datetime(2026, 8, 21, 9, 0),
        "likes": 44,
        "comments": 10,
        "views": 256,
        "views_24h": 45,
    },

    {
        "id": 8,
        "slug": "b-tree",
        "title": "B-Tree",

        "summary": "대량의 데이터를 효율적으로 검색하기 위해 데이터베이스 인덱스에서 널리 사용되는 트리입니다.",

        "content": """
B-Tree는 하나의 노드가 여러 개의 Key와 여러 개의 자식 노드를 가질 수 있는 균형 트리 자료구조입니다.

모든 Leaf Node가 동일한 깊이에 위치하도록 유지되기 때문에 데이터가 증가하더라도 트리의 높이가 지나치게 커지는 것을 방지할 수 있습니다.

디스크에서 데이터를 읽는 작업은 메모리 접근보다 비용이 크기 때문에, 한 번의 접근으로 많은 Key를 확인할 수 있는 B-Tree 구조가 데이터베이스에 적합합니다.

PostgreSQL을 비롯한 많은 데이터베이스에서는 인덱스를 구현하는 대표적인 자료구조로 B-Tree 계열을 사용합니다.
""",

        "tags": ["데이터베이스", "인덱스", "트리"],
        "author": "하린",
        "created_at": datetime(2026, 8, 20, 10, 30),
        "likes": 36,
        "comments": 8,
        "views": 211,
        "views_24h": 18,
    },

    {
        "id": 9,
        "slug": "http-https",
        "title": "HTTP와 HTTPS",

        "summary": "HTTP와 HTTPS의 차이와 TLS를 이용한 암호화 통신의 기본 원리를 알아봅니다.",

        "content": """
HTTP는 클라이언트와 서버가 웹에서 데이터를 주고받기 위한 프로토콜입니다.

일반 HTTP 통신은 전송되는 데이터 자체를 암호화하지 않기 때문에 중간에서 데이터를 확인하거나 변조할 가능성이 있습니다.

HTTPS는 HTTP 통신에 TLS를 적용하여 클라이언트와 서버 사이의 데이터를 암호화합니다.

또한 인증서를 이용해 사용자가 접속한 서버가 신뢰할 수 있는 서버인지 확인할 수 있으며, 통신 과정에서 데이터가 변경되었는지도 검증할 수 있습니다.

로그인 정보나 결제 정보처럼 민감한 데이터를 다루는 현대 웹 서비스에서는 HTTPS 사용이 사실상 기본입니다.
""",

        "tags": ["네트워크", "HTTP", "보안"],
        "author": "유진",
        "created_at": datetime(2026, 8, 17, 16, 0),
        "likes": 42,
        "comments": 6,
        "views": 275,
        "views_24h": 12,
    },
]