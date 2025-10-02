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
  GetCachePolicyRequest,
  GetCachePolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetCachePolicyCommandInput extends GetCachePolicyRequest {}
export interface GetCachePolicyCommandOutput
  extends GetCachePolicyResult,
    __MetadataBearer {}
export declare class GetCachePolicyCommand extends $Command<
  GetCachePolicyCommandInput,
  GetCachePolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetCachePolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetCachePolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetCachePolicyCommandInput, GetCachePolicyCommandOutput>;
  private serialize;
  private deserialize;
}
