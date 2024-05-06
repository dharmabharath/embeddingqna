from itertools import permutations,combinations
class Solution:
    def numRescueBoats(self, people,limit):
        ans=0
        while limit in people:
            ans+=1
            ss=people.index(limit)
            people.pop(ss)
        listans=[]
        for  i in range(1,limit+1):
            ss=set(combinations(people,i))
            for j in ss:
               if sum(j)==limit:
                   ans+=1
                   for k in j:
                       people.pop(people.index(k))
        ans+=len(people)
        print(ans)

people = [1,2]
limit = 3
obj=Solution()
obj.numRescueBoats(people,limit)
