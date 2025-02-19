from collections import defaultdict


class Mailbox:
    def __init__(self, pattern):
        self.pattern = pattern
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def each(self):
        msgs = self.messages.copy()
        self.messages.clear()
        return msgs


class World:
    def __init__(self):
        self.mailboxes = set()
        self.index = defaultdict(lambda: defaultdict(set))  # key -> value -> mailboxes
        self.keys_in_patterns = defaultdict(set)  # key -> mailboxes

    def sub(self, pattern):
        mailbox = Mailbox(pattern)
        self.mailboxes.add(mailbox)
        for k, v in pattern.items():
            self.index[k][v].add(mailbox)
            self.keys_in_patterns[k].add(mailbox)
        return mailbox

    def pub(self, message):
        candidates = set(self.mailboxes)
        items = []

        # 收集需要处理的键值对
        for k, v in message.items():
            if k not in self.keys_in_patterns:
                continue
            items.append((k, v))

        # 按候选集大小排序（优化过滤顺序）
        sorted_items = []
        for k, v in items:
            include_v = self.index[k].get(v, set())
            not_have_k = self.mailboxes - self.keys_in_patterns[k]
            current_candidates = include_v | not_have_k
            sorted_items.append((len(current_candidates), k, v))
        sorted_items.sort(key=lambda x: x[0])

        # 逐步过滤候选集
        for _, k, v in sorted_items:
            include_v = self.index[k].get(v, set())
            not_have_k = self.mailboxes - self.keys_in_patterns[k]
            current_candidates = include_v | not_have_k
            exclude = set()
            for other_v in self.index[k]:
                if other_v != v:
                    exclude.update(self.index[k][other_v])
            candidates &= (current_candidates - exclude)
            if not candidates:
                break

        # 精确匹配剩余候选集
        for mailbox in candidates:
            if all(message.get(pk) == pv for pk, pv in mailbox.pattern.items()):
                mailbox.add_message(message)

world = World()

# 订阅示例
sys_new = world.sub({"type": "new"})
sys_mouse = world.sub({"type": "mouse", "action": "move"})
sys_entity = world.sub({"eid": 42})

# 发布消息示例
world.pub({"type": "new", "eid": 42})         # sys_new和sys_entity会收到
world.pub({"type": "mouse", "action": "move", "x": 100})  # sys_mouse会收到

# 读取消息
for msg in sys_new.each():
    print("sys_new:", msg)
for msg in sys_mouse.each():
    print("sys_mouse:", msg)
for msg in sys_entity.each():
    print("sys_mouse:", msg)