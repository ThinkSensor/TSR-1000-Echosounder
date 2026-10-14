class TSRECHOSerial{
constructor({log=()=>{}}={}){this.log=log;this.q=new Uint8Array;this.running=false}
sleep(ms){return new Promise(r=>setTimeout(r,ms))}
append(b){let n=new Uint8Array(this.q.length+b.length);n.set(this.q);n.set(b,this.q.length);this.q=n}
take(n){let a=this.q.slice(0,n);this.q=this.q.slice(n);return a}
clear(){this.q=new Uint8Array}
join(a){let n=a.reduce((s,x)=>s+x.length,0),r=new Uint8Array(n),o=0;for(let x of a){r.set(x,o);o+=x.length}return r}
async connect(baud,filters=[]){let o={};if(filters.length)o.filters=filters;this.port=await navigator.serial.requestPort(o);await this.port.open({baudRate:baud});this.writer=this.port.writable.getWriter();this.running=true;this.loop();this.log("INFO",`Serial port opened at ${baud} baud`)}
async loop(){this.reader=this.port.readable.getReader();while(this.running){let {value,done}=await this.reader.read();if(done)break;if(value)this.append(value)}}
async disconnect(){this.running=false;try{await this.reader?.cancel()}catch(_){}try{this.reader?.releaseLock()}catch(_){}try{this.writer?.releaseLock()}catch(_){}try{await this.port?.close()}catch(_){}}
async write(s,label=s){this.log("TX",label);await this.writer.write(new TextEncoder().encode(s))}
async ack(){await this.writer.write(Uint8Array.of(0x47))}
async waitBytes(n,t=5000){let e=performance.now()+t;while(performance.now()<e){if(this.q.length>=n)return this.take(n);await this.sleep(2)}throw Error(`Timeout waiting for ${n} bytes (${this.q.length} buffered)`)}
async waitPlus(t){let e=performance.now()+t;while(performance.now()<e){if(this.q.length){let b=this.take(this.q.length);if(b.includes(43)){this.clear();return true}}await this.sleep(10)}this.clear();return false}
async prompt(label="command prompt"){this.clear();this.log("INFO",`Probing for ${label}`);for(let p=0;p<2;p++)for(let i=0;i<10;i++){await this.write("\r\n","<CR><LF>");if(await this.waitPlus(500)){this.log("INFO","Command prompt detected");await this.sleep(500);await this.write("\r\n","<CR><LF>");if(await this.waitPlus(500)){this.log("INFO",`${label} confirmed`);return true}break}}return false}
async readNul(t=5000){let e=performance.now()+t,a=[];while(performance.now()<e){if(this.q.length){let b=this.take(this.q.length),i=b.indexOf(0);if(i>=0){a.push(b.slice(0,i));this.clear();return this.join(a)}a.push(b)}await this.sleep(5)}throw Error("Timeout waiting for NUL")}
async c3(){this.clear();await this.write("C3\r\n","C3<CR><LF>");let s=new TextDecoder().decode(await this.readNul()),a=s.indexOf("{"),z=s.lastIndexOf("}");let j=s.slice(a,z+1);this.log("RX",j);return JSON.parse(j)}
async c2(x){let j=JSON.stringify(x);this.clear();await this.write(`C2,${j}\r\n`,`C2,${j}<CR><LF>`)}
async marker(t=10000){let e=performance.now()+t,n=0;while(performance.now()<e){if(this.q.length){let b=this.take(1)[0];if(b==82||b==70||b==77){if(n)this.log("INFO",`Discarded ${n} byte(s) before report marker`);return String.fromCharCode(b)}n++}else await this.sleep(2)}throw Error("Timed out waiting for R/F/M")}
header(rt,p,r){let q=new DataView(p.buffer,p.byteOffset,3),hs=q.getUint16(0,true),raw=q.getUint8(2),dt=raw>=49&&raw<=51?raw-48:raw;if(![1,2,3].includes(dt))throw Error("Bad datatype");let v=new DataView(r.buffer,r.byteOffset,r.byteLength);return{type:rt+dt,reportType:rt,dataTypeCode:dt,headerSize:hs,decimationFactor:v.getUint16(33,true),sendPacketSize:v.getUint16(35,true),dataSetLength:v.getUint32(37,true),numberOfDataSets:v.getUint16(41,true)}}
bytes(h,bpp){if(h.reportType=="F"&&h.decimationFactor){let n=h.dataSetLength*h.numberOfDataSets*8,d=h.decimationFactor*4;if(n%d)throw Error("Non-integral F byte count");return n/d}return h.dataSetLength*h.numberOfDataSets*bpp}
async report(mode,dec=1){
 dec=Math.max(1,Math.trunc(Number(dec)||1));
 let set;
 if(mode==="R") set={RunMode:0,DoFilter:0,DecimationFactor:0};
 else if(mode==="F") set={RunMode:0,DoFilter:1,DecimationFactor:dec};
 else if(mode==="M") set={RunMode:2,DoFilter:1,DecimationFactor:Math.max(8,dec)};
 else throw Error(`Invalid report mode ${mode}`);
 this.log("INFO",`Configuring ${mode}: RunMode=${set.RunMode}, DoFilter=${set.DoFilter}, DecimationFactor=${set.DecimationFactor}`);
 await this.c2(set);
 if(!await this.prompt("post-C2 command prompt"))throw Error("No prompt after C2");
 await this.write(`C4,${mode}\n`,`C4,${mode}<LF>`);
 let rt=await this.marker();if(rt!=mode)this.log("WARNING",`Requested ${mode} but sonar returned ${rt}`);
 let p=await this.waitBytes(3,10000),hs=new DataView(p.buffer,p.byteOffset,3).getUint16(0,true);if(hs<4||hs>1024)throw Error(`Invalid header size ${hs}`);
 let h=this.header(rt,p,await this.waitBytes(hs-4,10000)),bpp=h.dataTypeCode==2?2:4,count=this.bytes(h,bpp);
 this.log("INFO",`Header ${h.type}: decimation=${h.decimationFactor}, packet=${h.sendPacketSize}, frame=${h.dataSetLength}, datasets=${h.numberOfDataSets}, read=${count}`);
 let a=[],off=0,k=0;while(off<count){let n=Math.min(h.sendPacketSize,count-off),t=performance.now(),b=await this.waitBytes(n,10000);a.push(b);off+=n;k++;await this.ack();if(k==1||k%32==0||off==count)this.log("INFO",`Packet ${k}: ${n} bytes in ${(performance.now()-t).toFixed(1)} ms; ${off}/${count}; ACK G sent`)}
 let raw=this.join(a),per=raw.length/bpp/h.numberOfDataSets,v=new DataView(raw.buffer,raw.byteOffset,raw.byteLength),sets=[];
 for(let d=0;d<h.numberOfDataSets;d++){let x=h.dataTypeCode==1?new Float32Array(per):h.dataTypeCode==2?new Uint16Array(per):new Int32Array(per);for(let i=0;i<per;i++){let o=(d*per+i)*bpp;x[i]=h.dataTypeCode==1?v.getFloat32(o,true):h.dataTypeCode==2?v.getUint16(o,true):v.getInt32(o,true)}sets.push(x)}
 return{...h,datasets:sets,transmittedElementsPerSet:per,payloadBytes:count,appliedConfig:set}
}}
