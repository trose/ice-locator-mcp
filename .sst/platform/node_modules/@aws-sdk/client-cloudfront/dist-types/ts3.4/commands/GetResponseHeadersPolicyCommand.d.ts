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
  GetResponseHeadersPolicyRequest,
  GetResponseHeadersPolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetResponseHeadersPolicyCommandInput
  extends GetResponseHeadersPolicyRequest {}
export interface GetResponseHeadersPolicyCommandOutput
  extends GetResponseHeadersPolicyResult,
    __MetadataBearer {}
export declare class GetResponseHeadersPolicyCommand extends $Command<
  GetResponseHeadersPolicyCommandInput,
  GetResponseHeadersPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetResponseHeadersPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetResponseHeadersPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetResponseHeadersPolicyCommandInput,
    GetResponseHeadersPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
