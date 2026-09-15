package main

import (
 "encoding/json"
 "fmt"
 "os"
 "strings"
 "github.com/dotabuff/manta"
 "github.com/dotabuff/manta/dota"
)

func main() {
 f,err:=os.Open(os.Args[1]); if err!=nil {panic(err)}; defer f.Close()
 p,err:=manta.NewStreamParser(f); if err!=nil {panic(err)}
 enc:=json.NewEncoder(os.Stdout)
 var rules *manta.Entity
 targets:=[]float32{0,450,509,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,570,600,615,660,720,1110,1146,1286,2203,2205}
 next:=0
 p.OnEntity(func(e *manta.Entity, op manta.EntityOp) error {
  if e.GetClassName()=="CDOTAGamerulesProxy" {rules=e}
  return nil
 })
 p.Callbacks.OnCSVCMsg_PacketEntities(func(_ *dota.CSVCMsg_PacketEntities) error {
  if rules==nil || next>=len(targets) {return nil}
  start,_:=rules.GetFloat32("m_pGameRules.m_flGameStartTime")
  now,_:=rules.GetFloat32("m_pGameRules.m_fGameTime")
  if start<=0 || now-start<targets[next] {return nil}
  entities:=[]interface{}{}
  for _,e:=range p.FilterEntity(func(e *manta.Entity) bool {
   if e==nil {return false}
   n:=e.GetClassName(); return strings.HasPrefix(n,"CDOTA_Unit_Hero_") || strings.Contains(n,"Observer_Ward") || strings.Contains(n,"Tower") || strings.Contains(n,"Courier") || n=="CDOTA_PlayerResource" || strings.Contains(n,"DataDire") || strings.Contains(n,"DataRadiant")
  }) {
   linked:=map[string]interface{}{}
   for k,v:=range e.Map() {if strings.HasPrefix(k,"m_hItems.") || strings.HasPrefix(k,"m_hAbilities.") {
    var h uint64; switch n:=v.(type) {case uint64:h=n;case uint32:h=uint64(n); default:continue}
    if a:=p.FindEntityByHandle(h);a!=nil {
     nm:=""; if idx,ok:=a.GetInt32("m_pEntity.m_nameStringableIndex");ok {nm,_=p.LookupStringByIndex("EntityNames",idx)}
     linked[k]=map[string]interface{}{"class":a.GetClassName(),"name":nm,"state":a.Map()}
    }
   }}
   nm:="";if idx,ok:=e.GetInt32("m_pEntity.m_nameStringableIndex");ok {nm,_=p.LookupStringByIndex("EntityNames",idx)}
   entities=append(entities,map[string]interface{}{"index":e.GetIndex(),"serial":e.GetSerial(),"class":e.GetClassName(),"name":nm,"state":e.Map(),"linked":linked})
  }
  enc.Encode(map[string]interface{}{"target":targets[next],"game_time":now-start,"raw_time":now,"start_time":start,"tick":p.Tick,"build":p.GameBuild,"entities":entities,"rules":rules.Map()})
  next++
  return nil
 })
 p.Callbacks.OnCDemoFileInfo(func(m *dota.CDemoFileInfo) error {b,_:=json.MarshalIndent(m,"","  ");return os.WriteFile(os.Args[1]+".fileinfo.json",b,0644)})
 if err=p.Start();err!=nil {panic(err)}
 fmt.Fprintln(os.Stderr,"build",p.GameBuild,"tick",p.Tick)
}
