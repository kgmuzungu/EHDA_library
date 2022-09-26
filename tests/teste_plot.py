import pandas as pd
import matplotlib.pyplot as plt

liquids=["l1","l2","l2","Nayan","Reman"]
earnings={
    "var1 sjaak":[1,20,15,18,14],
    "var2 sjaak":[20,13,10,18,15],
    "var3 sjaak":[20,20,10,15,18],
}

df=pd.DataFrame(earnings,index=liquids)

df.plot(kind="bar",stacked=True,figsize=(10,8))
plt.legend(loc="lower left",bbox_to_anchor=(0.8,1.0))
plt.show()