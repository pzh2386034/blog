class RPC_RESORCE_ITEM
{
protected:

      VOS_UINT32        mRpcFunIndex;//功能索引
      rpc_call_smm      mRpcFuncall;//函数指针
      string            mFundes; //功能函数描述
      U8                mPrivilege;
      VOS_UINT32        mNeedOplog;    
      
public:
    /* 构造函数 */        
    RPC_RESORCE_ITEM( void );
    virtual ~RPC_RESORCE_ITEM( void );

public:

    /* 获取RPC函数指针 */
    virtual rpc_call_smm            GetRpcFuncall( void ) = 0;

    /* 本RPC是否需要记录日志，需要记录返回1，否则返回0，
       在多款处理日志中会掉用本函数判断是否需要记录日志 */
    virtual VOS_UINT32              GetRpcNeedTransLog( void ){return mNeedOplog;};

    /* 获取RPC的功能描述 */
    const string&                   GetRpcFunDescription( void );

    /* 克隆函数，返回本示例的拷贝 */
    virtual RPC_RESORCE_ITEM*       Clone(void)=0;

    /* 多框操作日志记录函数，如果GetRpcNeedTransLog 返回0，本函数就不会被调用 */
    virtual void                    RpcTransLog( const unsigned char* user_name, const unsigned char* user_ip, 
                                                      const unsigned char* usermode,  const unsigned int  chassic_number, 
                                                      const unsigned char* input, size_t inputlen, const unsigned char* output,
                                                      size_t    outputlen, unsigned int   func_id ){return;};

    /*多框统一鉴权函数*/
    virtual VOS_UINT32              RpcresUserDomainAuthority( const VOS_UCHAR* user_name, const VOS_UCHAR* user_ip,
                                                                       const VOS_UCHAR* usermode, const VOS_UCHAR  chassic_number,
                                                                       const VOS_UCHAR* input, SIZE_T inputlen,
                                                                       const VOS_UCHAR* output, SIZE_T outputlen,
                                                                       VOS_UINT32       func_id ) = 0;

    /*获取本RPC的用户权限*/
    virtual U8                      GetPrivilege(void){ return mPrivilege; };
    
    /*获取本RPC的索引ID*/
    virtual VOS_UINT32              GetRpcIdx(void){return mRpcFunIndex;};
};


class RpcResource
{
protected:

    typedef map<unsigned int, RPC_RESORCE_ITEM*>::iterator IterRpcResTab;

public:

    static VOS_INT32    LinkItem( RPC_RESORCE_ITEM* item );
    static VOS_INT32    AddItem( RPC_RESORCE_ITEM& item );
    static RPC_RESORCE_ITEM* FindItem( unsigned int rpc_index );

protected:

    RpcResource();
    static map<unsigned int, RPC_RESORCE_ITEM*> smRpcResTab;

};

/* 静态成员变量实例化 */
map<unsigned int, RPC_RESORCE_ITEM*> RpcResource::smRpcResTab;

/* 将RPC项目链接到管理中，参数指向的指针由RpcResource类内部管理，不能传入栈内存 */
VOS_INT32    RpcResource::LinkItem( RPC_RESORCE_ITEM* item )
{
    if( item == NULL )
    {
        return -1;
    }
    
    if( smRpcResTab.find( item->GetRpcIdx() ) != smRpcResTab.end() )
    {
        return -1;
    }

    smRpcResTab[item->GetRpcIdx()] = item;
    return 0;
}

/* 将RPC项目添加到管理中，函数内部会调用Clone生成一个拷贝 */
VOS_INT32    RpcResource::AddItem( RPC_RESORCE_ITEM& item )
{
    RPC_RESORCE_ITEM* insClone = item.Clone();
    if( !insClone )
    {
        return -1;
    }

    VOS_INT32 ret =  LinkItem( insClone );

    if( ret != 0 )
    {
        /* BEGIN: Modified by pWX310596, 2016/6/1 PN:DTS2016051711808 : */
        MEM_DELETE_NO_ARR(insClone);
        /* END:   Modified by pWX310596, 2016/6/1 */
    }

    return ret;
}

/* 根据rpc_index参数查找相应的item */
RPC_RESORCE_ITEM* RpcResource::FindItem( unsigned int rpc_index )
{
    IterRpcResTab iter = smRpcResTab.find( rpc_index );
    if( iter == smRpcResTab.end() )
    {
        return NULL;
    }

    return iter->second;
}





/*BEGIN:ADD by guankun 2017/7/24 水冷模式*/
DECLEAR_NEW_RPC_RES_ITEM(RPC_RES_GET_BLADE_COOLINGMODE_ITEM, GET_BLADE_COOLING_MODE, "get blade cooling mode", RPC_USER_COMMON, RPC_RES_NO_NEED_OPLOG)

/* 实现RPC功能函数指针获取函数，这个函数在rpc_server.c中会调用 */
rpc_call_smm RPC_RES_GET_BLADE_COOLINGMODE_ITEM::GetRpcFuncall( void )
{
    return rpccall_smmapi_get_coolingmode_ipmi;
};

/* 多框分权分域鉴权函数 */
VOS_UINT32 RPC_RES_GET_BLADE_COOLINGMODE_ITEM::RpcresUserDomainAuthority( const VOS_UCHAR* user_name,
                                                                               const VOS_UCHAR* user_ip,
                                                                               const VOS_UCHAR* usermode,
                                                                               const VOS_UCHAR  chassic_number,
                                                                               const VOS_UCHAR* input,
                                                                               SIZE_T           inputlen,
                                                                               const VOS_UCHAR* output,
                                                                               SIZE_T           outputlen,
                                                                               VOS_UINT32       func_id )
{
    call_authority_use_smm(OUTPUT_GETCOOLINGMODE_ST, funreturn)
};

/* 多框日志处理函数，如果不需要记录日志，则GetRpcNeedTransLog 函数返回为0，本函数直接返回即可  */
void  RPC_RES_GET_BLADE_COOLINGMODE_ITEM::RpcTransLog( const unsigned char* user_name, const unsigned char* user_ip, 
                                                       const unsigned char* usermode,  const unsigned int  chassic_number, 
                                                       const unsigned char* input, size_t inputlen, const unsigned char* output,
                                                       size_t    outputlen, unsigned int   func_id )
{
    return;
};





#define DECLEAR_NEW_RPC_RES_ITEM_GENERIC(item_name) \
class item_name : public RPC_RESORCE_ITEM \
{ \
public: \
    item_name(); \
    rpc_call_smm           GetRpcFuncall( void ); \
    void                   RpcTransLog(  RPC_TRANSLOG_ARGS ); \
    VOS_UINT32             RpcresUserDomainAuthority( const VOS_UCHAR*   user_name, const VOS_UCHAR* user_ip, \
                                                         const VOS_UCHAR* usermode,  const VOS_UCHAR  chassic_number, \
                                                         const VOS_UCHAR* input,     SIZE_T inputlen, \
                                                         const VOS_UCHAR* output,    SIZE_T outputlen, \
                                                         VOS_UINT32       func_id );\
    RPC_RESORCE_ITEM* Clone(){ return new item_name(); };\
};\


/* 派生类什么宏定义，使用此宏定义会生成构造函数 */
#define DECLEAR_NEW_RPC_RES_ITEM( item_name, rpc_id, rpc_description, privilege, need_oplog ) \
    DECLEAR_NEW_RPC_RES_ITEM_GENERIC(item_name) \
    item_name::item_name(){ mRpcFunIndex=rpc_id; mFundes=rpc_description;mPrivilege=privilege; mNeedOplog=need_oplog;};\
    
    
