import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  GetCachePolicyConfigRequest,
  GetCachePolicyConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetCachePolicyConfigCommandInput
  extends GetCachePolicyConfigRequest {}
export interface GetCachePolicyConfigCommandOutput
  extends GetCachePolicyConfigResult,
    __MetadataBearer {}
export declare class GetCachePolicyConfigCommand extends $Command<
  GetCachePolicyConfigCommandInput,
  GetCachePolicyConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetCachePolicyConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetCachePolicyConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetCachePolicyConfigCommandInput,
    GetCachePolicyConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
