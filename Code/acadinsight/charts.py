"""Self-contained Matplotlib charts - no internet or JS chart CDN needed."""
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .analytics import student_dashboard

INK='#152a41'; TEAL='#008d83'; CORAL='#ed875b'; PALE='#eef4f7'

def chart_png(student_id,kind='grades'):
    d=student_dashboard(student_id)
    subs=d['subjects']
    fig,ax=plt.subplots(figsize=(9,3.8),dpi=125)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    if kind=='grades':
        pairs=[(r['code'],r['percent']) for r in subs if r['percent'] is not None]
        title='Subject-wise final percentages'
        if pairs:
            x=np.arange(len(pairs)); ys=[v for _,v in pairs]
            ax.bar(x,ys,color=TEAL,width=.56)
            ax.set_xticks(x,[p[0] for p in pairs]); ax.set_ylim(0,110)
            for i,v in enumerate(ys):ax.text(i,v+2,f'{v:.1f}%',ha='center',fontsize=9,color=INK)
        else: ax.text(.5,.5,'No fully graded subjects yet',ha='center',va='center',transform=ax.transAxes)
    elif kind=='attendance':
        pairs=[(r['code'],r['attendance']['percentage']) for r in subs if r['attendance'] and r['attendance']['percentage'] is not None]
        title='Subject-wise attendance'
        if pairs:
            x=np.arange(len(pairs));ys=[v for _,v in pairs]
            ax.bar(x,ys,color=[TEAL if v>=d['settings']['attendance_threshold'] else CORAL for v in ys],width=.56)
            ax.axhline(d['settings']['attendance_threshold'], color='#aa6244',ls='--',lw=1,label='Configured threshold')
            ax.legend(loc='lower right',frameon=False,fontsize=8)
            ax.set_xticks(x,[p[0] for p in pairs]);ax.set_ylim(0,110)
            for i,v in enumerate(ys):ax.text(i,v+2,f'{v:.1f}%',ha='center',fontsize=9,color=INK)
        else:ax.text(.5,.5,'No recorded attendance yet',ha='center',va='center',transform=ax.transAxes)
    elif kind=='assessments':
        title='Assessment scores by subject (normalized to %)'
        legend=[]
        for r in subs:
            labels=[a['component'] for a in r['assessments']]
            values=[a['score_percent'] for a in r['assessments']]
            if values:
                ax.plot(range(len(values)),values,marker='o',lw=2,label=r['code'])
                legend.extend(labels)
        if legend:
            names=list(dict.fromkeys(legend))
            ax.set_xticks(list(range(len(names))),names)
            ax.set_ylim(0,105)
            ax.legend(loc='lower left',ncol=2,frameon=False,fontsize=8)
        else:ax.text(.5,.5,'No assessment scores yet',ha='center',va='center',transform=ax.transAxes)
    else:
        plt.close(fig);raise ValueError('Unknown chart type')
    ax.set_title(title,loc='left',fontweight='bold',fontsize=13,color=INK,pad=18)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#cedbe1')
    ax.tick_params(colors=INK,labelsize=9)
    ax.grid(axis='y',alpha=.13)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=2)
    out=io.BytesIO();fig.savefig(out,format='png',bbox_inches='tight',facecolor='white');plt.close(fig)
    return out.getvalue()
