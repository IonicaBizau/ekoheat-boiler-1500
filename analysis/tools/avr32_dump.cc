// Uses Ghidra's Apache-2.0 SLEIGH API. Linear disassembly, not code discovery.
#include "loadimage.hh"
#include "sleigh.hh"
#include <fstream>
#include <iostream>
#include <iterator>
using namespace ghidra;
class Image:public LoadImage {public:std::vector<uint1>b; uintb base; Image(const char*f,uintb a):LoadImage(f),base(a){std::ifstream in(f,std::ios::binary);b.assign(std::istreambuf_iterator<char>(in),{});} void loadFill(uint1*p,int4 n,const Address&a)override{for(int i=0;i<n;i++){auto k=a.getOffset()+i-base;p[i]=k<b.size()?b[k]:0;}} string getArchType()const override{return "avr32";} void adjustVma(long a)override{base+=a;}};
class Out:public AssemblyEmit{public:void dump(const Address&a,const string&m,const string&b)override{std::cout<<std::hex<<a.getOffset()<<"\t"<<m<<"\t"<<b;}};
int main(int argc,char**argv){if(argc<6)return 1;AttributeId::initialize();ElementId::initialize();Image img(argv[2],std::stoull(argv[3],0,0));ContextInternal ctx;Sleigh trans(&img,&ctx);DocumentStorage ds;std::istringstream xml(string("<sleigh>")+argv[1]+"</sleigh>");auto root=ds.parseDocument(xml)->getRoot();ds.registerTag(root);trans.initialize(ds);Out out;uintb p=std::stoull(argv[4],0,0),end=std::stoull(argv[5],0,0);while(p<end){Address a(trans.getDefaultCodeSpace(),p);try{int n=trans.printAssembly(out,a);std::cout<<"\t; bytes=";for(int j=0;j<n;j++)std::cout<<std::hex<<std::setw(2)<<std::setfill('0')<<(unsigned)img.b[p+j-img.base];std::cout<<"\n";p+=n;}catch(LowlevelError&e){std::cout<<std::hex<<p<<"\tINVALID\t"<<e.explain<<"\n";p+=2;}}}
