from pathlib import Path
import json,re,math,collections,hashlib
root=Path(__file__).parent
work=root.parent
files=['samsung_apple','samsung_extra','huawei_honor','china_catalog','china_extra','mi_current','mi_historical','oppo_foldables']
devices=[];coverage=[]
for name in files:
 p=work/(name+'.json')
 if not p.exists():continue
 a=json.loads(p.read_text())
 if isinstance(a,dict):
  coverage.append(a.get('coverageNotes',''));a=a.get('devices',[])
 devices+=a
# Backfill only explicitly present official screen resolutions missed by extraction.
texts={}
for name in ['spec_texts','more_specs','tail_specs','vivo_specs']:
 p=work/(name+'.json')
 if p.exists():
  a=json.loads(p.read_text())
  if isinstance(a,list):
   for it in a:
    if isinstance(it,list)and len(it)>1:texts[it[0]]=str(it[1])
for d in devices:
 if d['brand']=='OPPO'and len(d['screens'])==1 and not d['screens'][0].get('wpx'):
  for src in d['sources']:
   t=texts.get(src['url'],'');m=re.search(r'分辨率\s*(?:HD\+|FHD\+|QHD\+)?\s*(\d{3,4})\s*[×x*]\s*(\d{3,4})',t)
   if m:
    x,y=map(int,m.groups());d['screens'][0].update(wpx=min(x,y),hpx=max(x,y));break
# Earlier conversation reference devices, retained explicitly as historical references.
refs=[
 ('三星','Galaxy S21',2021,1080,2400,6.2,421,'https://www.samsung.com/hk_en/news/product/make-every-day-epic-with-galaxy-s21-and-galaxy-s21plus/'),
 ('三星','Galaxy A72',2021,1080,2400,6.7,394,'https://developer.samsung.com/galaxy-emulator-skin/galaxy-a.html'),
 ('苹果','iPhone 4',2010,640,960,3.5,326,'https://support.apple.com/zh-cn/112562'),
 ('苹果','iPhone 5',2012,640,1136,4,326,'https://support.apple.com/zh-cn/112016'),
 ('苹果','iPhone 6',2014,750,1334,4.7,326,'https://support.apple.com/zh-cn/111954'),
 ('苹果','iPhone 8',2017,750,1334,4.7,326,'https://support.apple.com/zh-cn/111976'),
 ('苹果','iPhone X',2017,1125,2436,5.85,458,'https://support.apple.com/zh-cn/111864'),
 ('苹果','iPhone 13',2021,1170,2532,6.06,460,'https://support.apple.com/zh-cn/111872'),
 ('苹果','iPhone 17 Pro',2025,1206,2622,6.27,460,'https://support.apple.com/zh-cn/125090'),
 ('苹果','iPhone 17 Pro Max',2025,1320,2868,6.86,460,'https://support.apple.com/zh-cn/125091'),
 ('小米','Xiaomi 15 Pro',2024,1440,3200,6.73,522,'https://www.mi.com/prod/xiaomi-15-pro'),
 ('小米','Xiaomi 15 Ultra',2025,1440,3200,6.73,522,'https://www.mi.com/global/product/xiaomi-15-ultra/specs/'),
 ('小米','Xiaomi 17 Pro',2025,1220,2656,6.3,464,'https://www.mi.com/prod/xiaomi-17-pro/specs'),
 ('小米','Xiaomi 17 Pro Max',2025,1200,2608,6.9,416,'https://www.mi.com/prod/xiaomi-17-pro-max/specs'),
]
for brand,model,year,w,h,diag,ppi,url in refs:
 kind='官方';sources=[{'title':'厂商公开规格 / 对话参考机型','url':url}]
 if model in ['Xiaomi 17 Pro','Xiaomi 17 Pro Max']:
  kind='公开';sources.append({'title':'公开规格（非厂商PPI直接核验）','url':'https://www.gsmarena.com/xiaomi_17_pro_'+('max_5g-14181.php'if'Max'in model else'5g-14182.php')})
 devices.append(dict(brand=brand,model=model,year=year,type='手机',form='直板',market='历史参考机型',body=None,bodyFold=None,bodyOpen=None,screens=[dict(name='主屏',wpx=w,hpx=h,diagonal=diag,ppi=ppi,ppiKind=kind,densityDpi=None,logical=None)],sources=sources,notes='此前对话的参考机型，单独保留用于尺寸对照，不作为当前在售证明。未独立核实的机身和逻辑配置留空。'))
def identity(d):
 model=re.sub(r'\s+','',d['model']).lower()
 model=re.sub(r'^(huawei|honor|xiaomi|oppo|samsung|荣耀|华为)','',model)
 return d['brand']+'|'+model
merged={}
for d in devices:
 key=identity(d)
 if key not in merged:merged[key]=d;continue
 old=merged[key]
 # Keep one record, enrich missing fields only, retain both provenances.
 for k in ['body','bodyFold','bodyOpen','year']:
  if not old.get(k)and d.get(k):old[k]=d[k]
 for s in d.get('screens',[]):
  match=next((x for x in old['screens']if x['name']==s['name']),None)
  if not match:old['screens'].append(s)
  else:
   for k,v in s.items():
    if not match.get(k)and v is not None:match[k]=v
 for src in d['sources']:
  if src['url']not in[x['url']for x in old['sources']]:old['sources'].append(src)
 old['notes']=old.get('notes','')+' '+d.get('notes','')
devices=list(merged.values())
reference_bodies={
 'Galaxy S21':('151.7×71.2×7.9 mm','https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2021_1Q_Interim_Report.pdf'),
 'Galaxy A72':('165.0×77.4×8.4 mm','https://www.samsung.com/ie/business/smartphones/galaxy-a/galaxy-a72-sm-a725fzwdeua/'),
 'iPhone 13':('146.7×71.5×7.65 mm','https://support.apple.com/zh-cn/111872'),
 'iPhone 17 Pro':('150.0×71.9×8.75 mm','https://support.apple.com/zh-cn/125090')
}
for d in devices:
 if d['model'] in reference_bodies and not d.get('body'):
  d['body'],body_source=reference_bodies[d['model']]
  d['sources'].append({'title':'官方机身尺寸','url':body_source})

release_index={}
for name in ['release_hh','release_sam_mi_apple','release_other']:
 p=work/(name+'.json')
 if not p.exists():continue
 entries=json.loads(p.read_text())
 if isinstance(entries,dict):entries=entries.get('devices',entries.get('dates',[]))
 for entry in entries:release_index[identity(entry)]=entry
for d in devices:
 d['id']='d-'+hashlib.sha1(identity(d).encode()).hexdigest()[:10]
 if d.get('year')and d['year']>2026:d['market']='待核实';d['notes']+=' 发布年份晚于截止日期，不计作已确认发布。'
 d['notes']=re.sub(r'\s+',' ',d.get('notes','')).strip()
 dateinfo=release_index.get(identity(d),{})
 for k in ['releaseDate','releaseMonth','announcementDate','releaseSource','releaseNote']:
  d[k]=dateinfo.get(k)
 for k in ['releaseDate','announcementDate']:
  if d.get(k):assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',d[k]),(d['model'],k,d[k])
 if d.get('releaseMonth'):assert re.fullmatch(r'\d{4}-\d{2}',d['releaseMonth']),(d['model'],d['releaseMonth'])
 if d.get('releaseDate')and d['releaseDate']>'2026-10-26':
  d['plannedReleaseDate']=d['releaseDate'];d['releaseDate']=None;d['market']='预售 / 尚未正式发售';d['notes']+=' 截至核查日尚未正式发售，计划首销：'+d['plannedReleaseDate']+'。'
 d['shipments']=None
 d['sources']=[s for s in d.get('sources',[])if re.match(r'^https?://',s.get('url',''))]
 for s in d['screens']:
  if s.get('densityDpi'):
   if s.get('wpx')and s.get('hpx'):s['logical']=f"{s['wpx']*160/s['densityDpi']:.2f}×{s['hpx']*160/s['densityDpi']:.2f} dp"
   s['logicalNote']='官方开发者文档对应初始配置；非实机当前读数'
  if s.get('ppiKind')=='计算'and s.get('diagonal')and s.get('wpx')and s.get('hpx'):
   s['ppi']=round((s['wpx']if s.get('shape')=='circle'else math.hypot(s['wpx'],s['hpx']))/s['diagonal'],3)
  for k in ['wpx','hpx','diagonal','ppi','densityDpi']:
   if s.get(k)is not None:
    assert isinstance(s[k],(int,float))and s[k]>0,(d['model'],k,s[k])
  if s.get('shape')=='circle':s['notes']='圆形屏：英寸为直径，分辨率为外接像素框；不能套矩形对角线公式。'
 # No guess at Android vs native HarmonyOS unit on a Huawei hardware name alone.
 if d['brand']=='驰为'and'Hi10'in d['model']:
  d['logicalUnit']='DIP / CSS px（Windows）';d['notes']+=' Windows二合一平板；Android dp不适用，需按Windows显示缩放读取逻辑尺寸。'
 elif d['brand']=='华为':d['logicalUnit']='dp / vp（依系统）'
 elif d['brand']=='苹果':d['logicalUnit']='pt'
 else:d['logicalUnit']='dp'
brand_order=['华为','荣耀','OPPO','小米','REDMI','三星','苹果','vivo','iQOO','一加','realme 真我','联想','摩托罗拉','红魔','努比亚','魅族','华硕 ROG','酷比魔方','台电','驰为']
def rank(d):
 known=bool(d['screens'][0].get('wpx')and d['screens'][0].get('hpx'))
 listed='当前'in d['market']or'列售'in d['market']
 return(not known,not listed,brand_order.index(d['brand'])if d['brand']in brand_order else 100,-(d['year']or 0),d['model'])
devices.sort(key=rank)
assert all(d['sources']for d in devices),'Every row needs provenance'
data={'title':'中国市场设备尺寸库','asOf':'2026-10-26','scope':'中国大陆官网目录与历史折叠屏；对话参考机型另列。非全渠道库存普查。','coverageNotes':'覆盖依据为厂商中国官网、开发者文档、历史规格存档及少量明确标注的公开历史资料。目录并不保证全部市场型号穷尽；官网购买入口不等于现货。教育平板、运营商与部分长尾品牌、特殊地区版、所有容量配色SKU和第三方库存仍有缺口。华为原生鸿蒙与旧系统逻辑单位不同；逻辑尺寸和密度仅在有依据时填写。','devices':devices}
output=Path('outputs/device-library');output.mkdir(parents=True,exist_ok=True)
encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\/')
template=(root/'template.html').read_text()
template=template.replace('</head>','<style>\n'+(root/'workbench.css').read_text()+'\n</style></head>')
template=template.replace('</body>','<script>\n'+(root/'workbench.js').read_text()+'\n</script></body>')
template=template.replace('已选 <b id="selected-count">0</b>/4','已选 <b id="selected-count">0</b>/12')
template=template.replace('selected.size>=4','selected.size>=12').replace('最多同时对比 4 款设备','最多同时对比 12 款设备')
template=template.replace("$('#show-compare').disabled=selected.size<2","$('#show-compare').disabled=selected.size<1")
# Physical dimensions display in 0.1mm, with sign-aware conventional rounding.
for key in ['width','height','diagWidth','diagHeight']:
 template=template.replace('fmt(m.'+key+',2)','phys(m.'+key+')')
template=template.replace('fmt(m.width-m.diagWidth,2)','phys(m.width-m.diagWidth)').replace('fmt(m.height-m.diagHeight,2)','phys(m.height-m.diagHeight)')
template=template.replace("${esc(v)}</div>`).join('')}</div>${d.screens", "${esc(k.includes('机身')?bodyText(v):v)}</div>`).join('')}</div>${d.screens")
assert template.count('__DEVICE_DATA__')==1
(output/'index.html').write_text(template.replace('__DEVICE_DATA__',encoded))
(root/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
scripts=re.findall(r'<script>([\s\S]*?)</script>',template)
(root/'app-check.js').write_text('\n'.join(scripts))
known=sum(bool(d['screens'][0].get('wpx')and d['screens'][0].get('hpx')and(d['screens'][0].get('diagonal')or d['screens'][0].get('ppi')))for d in devices)
summary={'models':len(devices),'brands':len({d['brand']for d in devices}),'screens':sum(len(d['screens'])for d in devices),'knownMainScreens':known,'releaseDates':sum(bool(d.get('releaseDate'))for d in devices),'releaseMonths':sum(bool(d.get('releaseMonth'))for d in devices),'announcements':sum(bool(d.get('announcementDate'))for d in devices),'foldables':sum(d['type']=='手机'and d['form']!='直板'for d in devices),'tablets':sum(d['type']=='平板'for d in devices),'densityKnown':sum(bool(s.get('densityDpi'))for d in devices for s in d['screens']),'byBrand':dict(collections.Counter(d['brand']for d in devices))}
(root/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
