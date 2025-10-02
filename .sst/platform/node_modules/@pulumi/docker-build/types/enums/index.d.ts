export declare const CacheMode: {
    /**
     * Only layers that are exported into the resulting image are cached.
     */
    readonly Min: "min";
    /**
     * All layers are cached, even those of intermediate steps.
     */
    readonly Max: "max";
};
export type CacheMode = (typeof CacheMode)[keyof typeof CacheMode];
export declare const CompressionType: {
    /**
     * Use `gzip` for compression.
     */
    readonly Gzip: "gzip";
    /**
     * Use `estargz` for compression.
     */
    readonly Estargz: "estargz";
    /**
     * Use `zstd` for compression.
     */
    readonly Zstd: "zstd";
};
export type CompressionType = (typeof CompressionType)[keyof typeof CompressionType];
export declare const NetworkMode: {
    /**
     * The default sandbox network mode.
     */
    readonly Default: "default";
    /**
     * Host network mode.
     */
    readonly Host: "host";
    /**
     * Disable network access.
     */
    readonly None: "none";
};
export type NetworkMode = (typeof NetworkMode)[keyof typeof NetworkMode];
export declare const Platform: {
    readonly Darwin_386: "darwin/386";
    readonly Darwin_amd64: "darwin/amd64";
    readonly Darwin_arm: "darwin/arm";
    readonly Darwin_arm64: "darwin/arm64";
    readonly Dragonfly_amd64: "dragonfly/amd64";
    readonly Freebsd_386: "freebsd/386";
    readonly Freebsd_amd64: "freebsd/amd64";
    readonly Freebsd_arm: "freebsd/arm";
    readonly Linux_386: "linux/386";
    readonly Linux_amd64: "linux/amd64";
    readonly Linux_arm: "linux/arm";
    readonly Linux_arm64: "linux/arm64";
    readonly Linux_mips64: "linux/mips64";
    readonly Linux_mips64le: "linux/mips64le";
    readonly Linux_ppc64le: "linux/ppc64le";
    readonly Linux_riscv64: "linux/riscv64";
    readonly Linux_s390x: "linux/s390x";
    readonly Netbsd_386: "netbsd/386";
    readonly Netbsd_amd64: "netbsd/amd64";
    readonly Netbsd_arm: "netbsd/arm";
    readonly Openbsd_386: "openbsd/386";
    readonly Openbsd_amd64: "openbsd/amd64";
    readonly Openbsd_arm: "openbsd/arm";
    readonly Plan9_386: "plan9/386";
    readonly Plan9_amd64: "plan9/amd64";
    readonly Solaris_amd64: "solaris/amd64";
    readonly Windows_386: "windows/386";
    readonly Windows_amd64: "windows/amd64";
};
export type Platform = (typeof Platform)[keyof typeof Platform];
