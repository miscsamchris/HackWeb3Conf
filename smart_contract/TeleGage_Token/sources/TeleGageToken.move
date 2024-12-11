module TeleGageToken::telegage_token {
    struct TeleGageToken {}

    fun init_module(sender: &signer) {
        aptos_framework::managed_coin::initialize<TeleGageToken>(
            sender,
            b"TeleGage Token",
            b"TELE",
            6,
            false,
        );
    }
}