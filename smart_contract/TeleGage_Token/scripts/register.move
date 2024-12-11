//:!:>moon
script {
    fun register(account: &signer) {
        aptos_framework::managed_coin::register<TeleGageToken::telegage_token::TeleGageToken>(account)
    }
}
//<:!:moon