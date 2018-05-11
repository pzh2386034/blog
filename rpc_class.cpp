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

