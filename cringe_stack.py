class Node:
    def __init__(self):
        self.data = None
        self.next = None


class Stack:

    def __init__(self):
        self.head = None

    def pop(self):
        head = self.head
        self.head = self.head.next
        return head.data

    def push(self, obj):
        new = Node()
        new.data = obj
        new.next = self.head
        self.head = new

    def show(self):
        temp = self.head
        while temp is not None:
            print(temp.data, '->' if temp.next is not None else '', end=' ')
            temp = temp.next
        print('\n')

    def peek(self):
        return self.head.data


# st = Stack()
#
# st.push(obj=1)
# st.push(obj=2)
# st.push(obj=3)
# st.push(obj=4)
#
# st.show()
#
# st.pop()
# st.pop()
# st.pop()
#
# st.show()
