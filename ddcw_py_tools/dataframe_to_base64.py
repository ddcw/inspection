# -*- coding: utf-8 -*-

import io
import base64
def get_base64(df,pic_type):
	tmps_ = io.BytesIO()
	if pic_type == "bar":
		tp_plt = df.plot()
		tp_plt.plot(kind=pic_type,yticks=[]).get_figure().savefig(tmps_,format='png', bbox_inches="tight")
		return base64.b64encode(tmps_.getvalue()).decode("utf-8").replace("\n", "")
	elif pic_type == "barh":
		tp_plt = df.plot(kind=pic_type, ylabel="", xlabel="", legend=False ) #ylabel=""设置y标签为空, legend=False不显示右上角的说明
		for i, v in enumerate(df.values):
		        tp_plt.text(v, i, str(v), color='blue', fontweight='bold')
		tp_plt.get_figure().savefig(tmps_,format='png', bbox_inches="tight")
		return base64.b64encode(tmps_.getvalue()).decode("utf-8").replace("\n", "")
	elif pic_type == "pie":
		df.plot(kind=pic_type,subplots=True,figsize=(6,6),xlabel="",ylabel="")[0].get_figure().savefig(tmps_,format='png', bbox_inches="tight")
		return base64.b64encode(tmps_.getvalue()).decode("utf-8").replace("\n", "")
	elif pic_type == "area":
		df.plot(kind=pic_type,).get_figure().savefig(tmps_,format='png', bbox_inches="tight")
		return base64.b64encode(tmps_.getvalue()).decode("utf-8").replace("\n", "")
	else:
		return False
