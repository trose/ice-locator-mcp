import * as pulumi from "@pulumi/pulumi";
import * as inputs from "./types/input";
import * as outputs from "./types/output";
/**
 * A wrapper around `docker buildx imagetools create` to create an index
 * (or manifest list) referencing one or more existing images.
 *
 * In most cases you do not need an `Index` to build a multi-platform
 * image -- specifying multiple platforms on the `Image` will handle this
 * for you automatically.
 *
 * However, as of April 2024, building multi-platform images _with
 * caching_ will only export a cache for one platform at a time (see [this
 * discussion](https://github.com/docker/buildx/discussions/1382) for more
 * details).
 *
 * Therefore this resource can be helpful if you are building
 * multi-platform images with caching: each platform can be built and
 * cached separately, and an `Index` can join them all together. An
 * example of this is shown below.
 *
 * This resource creates an OCI image index or a Docker manifest list
 * depending on the media types of the source images.
 *
 * ## Example Usage
 * ### Multi-platform registry caching
 *
 * ```typescript
 * import * as pulumi from "@pulumi/pulumi";
 * import * as docker_build from "@pulumi/docker-build";
 *
 * const amd64 = new docker_build.Image("amd64", {
 *     cacheFrom: [{
 *         registry: {
 *             ref: "docker.io/pulumi/pulumi:cache-amd64",
 *         },
 *     }],
 *     cacheTo: [{
 *         registry: {
 *             mode: docker_build.CacheMode.Max,
 *             ref: "docker.io/pulumi/pulumi:cache-amd64",
 *         },
 *     }],
 *     context: {
 *         location: "app",
 *     },
 *     platforms: [docker_build.Platform.Linux_amd64],
 *     tags: ["docker.io/pulumi/pulumi:3.107.0-amd64"],
 * });
 * const arm64 = new docker_build.Image("arm64", {
 *     cacheFrom: [{
 *         registry: {
 *             ref: "docker.io/pulumi/pulumi:cache-arm64",
 *         },
 *     }],
 *     cacheTo: [{
 *         registry: {
 *             mode: docker_build.CacheMode.Max,
 *             ref: "docker.io/pulumi/pulumi:cache-arm64",
 *         },
 *     }],
 *     context: {
 *         location: "app",
 *     },
 *     platforms: [docker_build.Platform.Linux_arm64],
 *     tags: ["docker.io/pulumi/pulumi:3.107.0-arm64"],
 * });
 * const index = new docker_build.Index("index", {
 *     sources: [
 *         amd64.ref,
 *         arm64.ref,
 *     ],
 *     tag: "docker.io/pulumi/pulumi:3.107.0",
 * });
 * export const ref = index.ref;
 * ```
 */
export declare class Index extends pulumi.CustomResource {
    /**
     * Get an existing Index resource's state with the given name, ID, and optional extra
     * properties used to qualify the lookup.
     *
     * @param name The _unique_ name of the resulting resource.
     * @param id The _unique_ provider ID of the resource to lookup.
     * @param opts Optional settings to control the behavior of the CustomResource.
     */
    static get(name: string, id: pulumi.Input<pulumi.ID>, opts?: pulumi.CustomResourceOptions): Index;
    /**
     * Returns true if the given object is an instance of Index.  This is designed to work even
     * when multiple copies of the Pulumi SDK have been loaded into the same process.
     */
    static isInstance(obj: any): obj is Index;
    /**
     * If true, push the index to the target registry.
     *
     * Defaults to `true`.
     */
    readonly push: pulumi.Output<boolean | undefined>;
    /**
     * The pushed tag with digest.
     *
     * Identical to the tag if the index was not pushed.
     */
    readonly ref: pulumi.Output<string>;
    /**
     * Authentication for the registry where the tagged index will be pushed.
     *
     * Credentials can also be included with the provider's configuration.
     */
    readonly registry: pulumi.Output<outputs.Registry | undefined>;
    /**
     * Existing images to include in the index.
     */
    readonly sources: pulumi.Output<string[]>;
    /**
     * The tag to apply to the index.
     */
    readonly tag: pulumi.Output<string>;
    /**
     * Create a Index resource with the given unique name, arguments, and options.
     *
     * @param name The _unique_ name of the resource.
     * @param args The arguments to use to populate this resource's properties.
     * @param opts A bag of options that control this resource's behavior.
     */
    constructor(name: string, args: IndexArgs, opts?: pulumi.CustomResourceOptions);
}
/**
 * The set of arguments for constructing a Index resource.
 */
export interface IndexArgs {
    /**
     * If true, push the index to the target registry.
     *
     * Defaults to `true`.
     */
    push?: pulumi.Input<boolean>;
    /**
     * Authentication for the registry where the tagged index will be pushed.
     *
     * Credentials can also be included with the provider's configuration.
     */
    registry?: pulumi.Input<inputs.RegistryArgs>;
    /**
     * Existing images to include in the index.
     */
    sources: pulumi.Input<pulumi.Input<string>[]>;
    /**
     * The tag to apply to the index.
     */
    tag: pulumi.Input<string>;
}
