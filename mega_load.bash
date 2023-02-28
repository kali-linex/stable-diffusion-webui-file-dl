if command -v mega-get || [ -f megacmd/usr/bin/mega-get ]; then
    echo MEGAcmd already installed.
    exit 0
fi
if ! command -v zstd; then
    echo '`zstd` is required for automagically installing MEGAcmd. Alternatively, install it manually. Disabling MEGA support.'
    exit 0
fi
wget https://mega.nz/linux/repo/Arch_Extra/x86_64/megacmd-1.5.1-2-x86_64.pkg.tar.zst -O megacmd.tar.zst
mkdir -p megacmd
tar -C megacmd xf megacmd.tar.zst