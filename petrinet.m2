root=Petrinet()
p1=Place(of=root, name="p1", tokens=1)
p2=Place(of=root, name="p2", tokens=0)
t=Transition(of=root)
ToTransition(source=p1, dest=t, weight=1)
FromTransition(source=t, dest=p2, weight=1)

